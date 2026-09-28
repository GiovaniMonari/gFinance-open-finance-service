import asyncio

from app.accounts.service import AccountService
from app.connections.providers.mock import MockOpenFinanceProvider
from app.database.postgres import connect_postgres
from app.repositories.account_repository import (
    PostgreSQLAccountRepository,
)


async def main():

    pool = await connect_postgres()

    try:
        provider = MockOpenFinanceProvider()

        repository = PostgreSQLAccountRepository(
            pool
        )

        service = AccountService(
            provider=provider,
            repository=repository,
        )

        accounts = await service.sync_accounts(
            connection_id="00000000-0000-0000-0000-000000000001",
            user_id="00000000-0000-0000-0000-000000000001",
        )

        for account in accounts:
            print(account)

    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())