import asyncio

from app.connections.providers.mock import MockOpenFinanceProvider
from app.normalization.transaction_normalizer import TransactionNormalizer
from app.synchronization.service import SynchronizationService
from app.messaging.rabbitmq import connect_rabbitmq


async def main():
    provider = MockOpenFinanceProvider()
    normalizer = TransactionNormalizer()

    service = SynchronizationService(
        provider=provider,
        normalizer=normalizer,
    )

    rabbitmq = await connect_rabbitmq()

    transactions = await service.sync_connection(
        connection_id="mock-connection-user-001",
        user_id="user-001",
        rabbitmq_connection=rabbitmq,
        provider_name="mock-provider",
    )

    for transaction in transactions:
        print(transaction)

    await rabbitmq.close()


asyncio.run(main())