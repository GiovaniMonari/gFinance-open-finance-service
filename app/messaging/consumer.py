import json
import aio_pika

from app.transactions.models import BankTransaction
from app.repositories.transaction_repository import (
    PostgreSQLTransactionRepository,
)

from app.synchronization.service import SynchronizationService

from app.connections.providers.factory import get_open_finance_provider
from app.repositories.connection_repository import (
    PostgreSQLConnectionRepository,
)
from app.repositories.account_repository import (
    PostgreSQLAccountRepository,
)
from app.repositories.transaction_repository import (
    PostgreSQLTransactionRepository,
)
from app.normalization.transaction_normalizer import TransactionNormalizer
from app.transactions.service import TransactionService

from app.repositories.sync_repository import (
    PostgreSQLSynchronizationRepository,
)
from app.synchronization.models import SyncStatus
from app.messaging.publisher import publish_event
from app.messaging.events import EventType

from app.synchronization.retry import execute_with_retry

async def start_consumer(
    connection,
    postgres,
):
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "Econva.events",
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )

    queue = await channel.declare_queue(
        "transactions",
        durable=True,
    )

    await queue.bind(
        exchange,
        routing_key="transaction.created",
    )

    repository = PostgreSQLTransactionRepository(
        postgres
    )

    async with queue.iterator() as messages:
        async for message in messages:
            async with message.process():

                data = json.loads(message.body)

                transaction = BankTransaction(
                    **data
                )

                await repository.create(
                    transaction
                )

                print(
                    f"Transaction persisted: "
                    f"{transaction.external_id}"
                )

async def start_sync_completed_consumer(connection):
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "Econva.events",
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )

    queue = await channel.declare_queue(
        "sync.completed",
        durable=True,
    )

    await queue.bind(
        exchange,
        routing_key="account.sync.completed",
    )

    async with queue.iterator() as messages:
        async for message in messages:
            async with message.process():
                data = json.loads(message.body)

                print(
                    "Synchronization completed:",
                    data,
                )

async def start_sync_requested_consumer(
    connection,
    postgres,
):
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "Econva.events",
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )

    queue = await channel.declare_queue(
        "sync.requested",
        durable=True,
    )

    await queue.bind(
        exchange,
        routing_key="account.sync.requested",
    )

    async with queue.iterator() as messages:
        async for message in messages:
            async with message.process():

                data = json.loads(message.body)

                connection_id = data["connection_id"]
                user_id = data["user_id"]
                job_id = data["job_id"]

                sync_repository = PostgreSQLSynchronizationRepository(
                    postgres
                )

                await sync_repository.update_status(
                    job_id=job_id,
                    status=SyncStatus.PROCESSING,
                )

                print(
                    "Synchronization requested:",
                    data,
                )

                provider = get_open_finance_provider(
                    connection_repository=connection_repository
                )

                connection_repository = (
                    PostgreSQLConnectionRepository(postgres)
                )

                account_repository = (
                    PostgreSQLAccountRepository(postgres)
                )

                transaction_repository = (
                    PostgreSQLTransactionRepository(postgres)
                )

                transaction_service = TransactionService(
                    provider=provider,
                    normalizer=TransactionNormalizer(),
                    account_repository=account_repository,
                    transaction_repository=transaction_repository,
                    connection_repository=connection_repository,
                )

                synchronization_service = SynchronizationService(
                    provider=provider,
                    connection_repository=connection_repository,
                    account_repository=account_repository,
                    transaction_service=transaction_service,
                )

                try:
                    result = await execute_with_retry(
                        lambda: synchronization_service.sync_connection(
                            connection_id=connection_id,
                            user_id=user_id,
                            rabbitmq_connection=connection,
                            job_id=job_id,
                        )
                    )

                    await sync_repository.update_status(
                        job_id=job_id,
                        status=SyncStatus.COMPLETED,
                        accounts_count=len(result["accounts"]),
                        transactions_count=len(result["transactions"]),
                    )

                except Exception as error:

                    await sync_repository.update_status(
                        job_id=job_id,
                        status=SyncStatus.FAILED,
                        error=str(error),
                    )

                    await publish_event(
                        connection=connection,
                        event_type=EventType.ACCOUNT_SYNC_FAILED,
                        payload={
                            "job_id": job_id,
                            "connection_id": connection_id,
                            "user_id": user_id,
                            "error": str(error),
                        },
                    )

                    print(
                        "Synchronization failed:",
                        error,
                    )

async def start_sync_failed_consumer(connection):

    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "Econva.events",
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )

    queue = await channel.declare_queue(
        "sync.failed",
        durable=True,
    )

    await queue.bind(
        exchange,
        routing_key="account.sync.failed",
    )

    async with queue.iterator() as messages:
        async for message in messages:

            async with message.process():

                data = json.loads(message.body)

                print(
                    "Synchronization failed:",
                    data,
                )