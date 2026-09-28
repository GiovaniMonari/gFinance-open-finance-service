from app.accounts.service import AccountService
from app.connections.providers.base import OpenFinanceProvider
from app.repositories.connection_repository import ConnectionRepository
from app.repositories.account_repository import AccountRepository
from app.transactions.service import TransactionService
from app.messaging.publisher import publish_event
from app.messaging.events import EventType

class SynchronizationService:
    def __init__(
        self,
        provider: OpenFinanceProvider,
        connection_repository: ConnectionRepository,
        account_repository: AccountRepository,
        transaction_service: TransactionService,
    ):
        self.provider = provider
        self.connection_repository = connection_repository
        self.account_repository = account_repository
        self.transaction_service = transaction_service

    async def sync_connection(
        self,
        connection_id: str,
        user_id: str,
        rabbitmq_connection,
         job_id: str,
    ):
        connection = await self.connection_repository.find_by_id(
            connection_id
        )

        if not connection:
            raise ValueError(
                f"Conexão não encontrada: {connection_id}"
            )

        account_service = AccountService(
            provider=self.provider,
            repository=self.account_repository,
        )

        accounts = await account_service.sync_accounts(
            connection_id=connection_id,
            user_id=user_id,
        )

        transactions = []

        for account in accounts:
            account_transactions = await self.transaction_service.sync_transactions(
                account_id=account.id,
                user_id=user_id,
                rabbitmq_connection=rabbitmq_connection,
                provider_name=self.provider.name,
            )

            transactions.extend(account_transactions)

        await publish_event(
            connection=rabbitmq_connection,
            event_type=EventType.ACCOUNT_SYNC_COMPLETED,
            payload={
                "connection_id": connection_id,
                "user_id": user_id,
                "accounts_count": len(accounts),
                "transactions_count": len(transactions),
                "job_id": job_id,
            },
        )
        
        return {
            "connection": connection,
            "accounts": accounts,
            "transactions": transactions,
        }