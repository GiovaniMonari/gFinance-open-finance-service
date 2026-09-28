from app.connections.providers.base import OpenFinanceProvider
from app.normalization.transaction_normalizer import TransactionNormalizer
from app.messaging.publisher import publish_transaction
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.connection_repository import ConnectionRepository

class TransactionService:

    def __init__(
        self,
        provider: OpenFinanceProvider,
        normalizer: TransactionNormalizer,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
        connection_repository: ConnectionRepository,
    ):
        self.provider = provider
        self.normalizer = normalizer
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.connection_repository = connection_repository

    async def sync_transactions(
        self,
        account_id: str,
        user_id: str,
        rabbitmq_connection,
        provider_name: str,
    ):
        account = await self.account_repository.find_by_id(
            account_id
        )

        last_synced_at = await self.connection_repository.get_last_synced_at(
            account.connection_id
        )

        if not account:
            raise ValueError(
                f"Conta não encontrada: {account_external_id}"
            )

        transactions = await self.provider.get_transactions(
            account.external_id,
            since=last_synced_at,
        )

        normalized_transactions = []

        for transaction in transactions:
            normalized = self.normalizer.normalize(
                transaction=transaction,
                user_id=user_id,
                account_id=account.id,
                provider=provider_name,
            )

            await publish_transaction(
                rabbitmq_connection,
                normalized.model_dump(mode="json"),
            )

            normalized_transactions.append(normalized)


        await self.connection_repository.update_last_synced_at(
            connection_id=account.connection_id,
        )

        return normalized_transactions

    async def get_transactions(
        self,
        account_id: str,
    ):
        account = await self.account_repository.find_by_id(
            account_id
        )

        if not account:
            raise ValueError(
                f"Conta não encontrada: {account_id}"
            )

        return await self.transaction_repository.find_by_account_id(
            account.id
        )