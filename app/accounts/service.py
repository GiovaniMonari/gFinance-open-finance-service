import uuid

from app.accounts.models import BankAccount
from app.connections.providers.base import OpenFinanceProvider
from app.repositories.account_repository import AccountRepository


class AccountService:

    def __init__(
        self,
        provider: OpenFinanceProvider,
        repository: AccountRepository,
    ):
        self.provider = provider
        self.repository = repository

    async def sync_accounts(
        self,
        connection_id: str,
        user_id: str,
    ) -> list[BankAccount]:

        provider_accounts = await self.provider.get_accounts(
            connection_id
        )

        accounts = []

        for provider_account in provider_accounts:
            account = BankAccount(
                id=str(uuid.uuid4()),
                connection_id=connection_id,
                user_id=user_id,
                external_id=provider_account["external_id"],
                name=provider_account["name"],
                bank_name=provider_account["bank_name"],
                account_type=provider_account["account_type"],
                balance=provider_account.get("balance"),
            )

            account = await self.repository.create(
                account
            )

            accounts.append(account)

        return accounts