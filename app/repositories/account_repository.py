from abc import ABC, abstractmethod

import asyncpg

from app.accounts.models import BankAccount


class AccountRepository(ABC):

    @abstractmethod
    async def create(
        self,
        account: BankAccount,
    ) -> BankAccount:
        pass

    @abstractmethod
    async def find_by_connection_id(
        self,
        connection_id: str,
    ) -> list[BankAccount]:
        pass

    @abstractmethod
    async def find_by_external_id(
        self,
        external_id: str,
    ) -> BankAccount | None:
        pass

    @abstractmethod
    async def find_by_id(
        self,
        account_id: str,
    ) -> BankAccount | None:
        pass


class PostgreSQLAccountRepository(AccountRepository):

    def __init__(
        self,
        pool: asyncpg.Pool,
    ):
        self.pool = pool

    async def create(
        self,
        account: BankAccount,
    ) -> BankAccount:

        query = """
            INSERT INTO open_finance_accounts (
                id,
                connection_id,
                user_id,
                external_id,
                name,
                bank_name,
                account_type,
                balance
            )
            VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8
            )
            ON CONFLICT (connection_id, external_id)
            DO UPDATE SET
                name = EXCLUDED.name,
                bank_name = EXCLUDED.bank_name,
                account_type = EXCLUDED.account_type,
                balance = EXCLUDED.balance,
                updated_at = CURRENT_TIMESTAMP
            RETURNING
                id,
                connection_id,
                user_id,
                external_id,
                name,
                bank_name,
                account_type,
                balance
        """

        async with self.pool.acquire() as db:
            row = await db.fetchrow(
                query,
                account.id,
                account.connection_id,
                account.user_id,
                account.external_id,
                account.name,
                account.bank_name,
                account.account_type,
                account.balance,
            )

        return BankAccount(
            id=str(row["id"]),
            connection_id=str(row["connection_id"]),
            user_id=str(row["user_id"]),
            external_id=row["external_id"],
            name=row["name"],
            bank_name=row["bank_name"],
            account_type=row["account_type"],
            balance=float(row["balance"])
            if row["balance"] is not None
            else None,
        )

    async def find_by_connection_id(
        self,
        connection_id: str,
    ) -> list[BankAccount]:

        query = """
            SELECT
                id,
                connection_id,
                user_id,
                external_id,
                name,
                bank_name,
                account_type,
                balance
            FROM open_finance_accounts
            WHERE connection_id = $1
        """

        async with self.pool.acquire() as db:
            rows = await db.fetch(
                query,
                connection_id,
            )

        return [
            BankAccount(
                id=str(row["id"]),
                connection_id=str(row["connection_id"]),
                user_id=str(row["user_id"]),
                external_id=row["external_id"],
                name=row["name"],
                bank_name=row["bank_name"],
                account_type=row["account_type"],
                balance=float(row["balance"])
                if row["balance"] is not None
                else None,
            )
            for row in rows
        ]

    async def find_by_external_id(
        self,
        external_id: str,
    ) -> BankAccount | None:

        query = """
            SELECT
                id,
                connection_id,
                user_id,
                external_id,
                name,
                bank_name,
                account_type,
                balance
            FROM open_finance_accounts
            WHERE external_id = $1
        """

        async with self.pool.acquire() as db:
            row = await db.fetchrow(
                query,
                external_id,
            )

        if not row:
            return None

        return BankAccount(
            id=str(row["id"]),
            connection_id=str(row["connection_id"]),
            user_id=str(row["user_id"]),
            external_id=row["external_id"],
            name=row["name"],
            bank_name=row["bank_name"],
            account_type=row["account_type"],
            balance=float(row["balance"])
            if row["balance"] is not None
            else None,
        )

    async def find_by_id(
        self,
        account_id: str,
    ) -> BankAccount | None:

        query = """
            SELECT
                id,
                connection_id,
                user_id,
                external_id,
                name,
                bank_name,
                account_type,
                balance
            FROM open_finance_accounts
            WHERE id = $1
        """

        async with self.pool.acquire() as db:
            row = await db.fetchrow(
                query,
                account_id,
            )

        if not row:
            return None

        return BankAccount(
            id=str(row["id"]),
            connection_id=str(row["connection_id"]),
            user_id=str(row["user_id"]),
            external_id=row["external_id"],
            name=row["name"],
            bank_name=row["bank_name"],
            account_type=row["account_type"],
            balance=float(row["balance"])
            if row["balance"] is not None
            else None,
        )