from abc import ABC, abstractmethod
import uuid

import asyncpg

from app.transactions.models import BankTransaction


class TransactionRepository(ABC):

    @abstractmethod
    async def create(
        self,
        transaction: BankTransaction,
    ) -> BankTransaction:
        pass

    @abstractmethod
    async def find_by_account_id(
        self,
        account_id: str,
    ) -> list[BankTransaction]:
        pass

    @abstractmethod
    async def delete_by_connection_id(
        self,
        connection_id: str,
    ) -> None:
        """Drop every transaction stored for this link's accounts.

        Scoped by connection rather than by user on purpose: the call is
        reached only from a disconnection that was already scoped to one
        owner, and the subquery names the accounts of that one link.
        """
        pass


class PostgreSQLTransactionRepository(TransactionRepository):

    def __init__(
        self,
        pool: asyncpg.Pool,
    ):
        self.pool = pool

    async def create(
        self,
        transaction: BankTransaction,
    ) -> BankTransaction:

        transaction_id = str(uuid.uuid4())

        query = """
            INSERT INTO open_finance_transactions (
                id,
                account_id,
                user_id,
                external_id,
                provider,
                amount,
                description,
                transaction_date,
                type,
                category,
                source
            )
            VALUES (
                $1, $2, $3, $4, $5,
                $6, $7, $8, $9, $10, $11
            )
            ON CONFLICT (provider, external_id)
            DO UPDATE SET
                amount = EXCLUDED.amount,
                description = EXCLUDED.description,
                transaction_date = EXCLUDED.transaction_date,
                type = EXCLUDED.type,
                category = EXCLUDED.category,
                updated_at = CURRENT_TIMESTAMP
        """

        async with self.pool.acquire() as db:
            await db.execute(
                query,
                transaction_id,
                transaction.account_id,
                transaction.user_id,
                transaction.external_id,
                transaction.provider,
                transaction.amount,
                transaction.description,
                transaction.date,
                transaction.type,
                transaction.category,
                transaction.source,
            )

        return transaction

    async def find_by_account_id(
        self,
        account_id: str,
    ) -> list[BankTransaction]:

        query = """
            SELECT
                external_id,
                account_id,
                user_id,
                amount,
                description,
                transaction_date,
                type,
                category,
                provider,
                source
            FROM open_finance_transactions
            WHERE account_id = $1
            ORDER BY transaction_date DESC
        """

        async with self.pool.acquire() as db:
            rows = await db.fetch(
                query,
                account_id,
            )

        return [
        BankTransaction(
            external_id=row["external_id"],
            account_id=str(row["account_id"]),
            user_id=str(row["user_id"]),
            amount=float(row["amount"]),
            description=row["description"],
            date=row["transaction_date"],
            type=row["type"],
            category=row["category"],
            provider=row["provider"],
            source=row["source"],
        )
        for row in rows
    ]

    async def delete_by_connection_id(
        self,
        connection_id: str,
    ) -> None:

        query = """
            DELETE FROM open_finance_transactions
            WHERE account_id IN (
                SELECT id
                FROM open_finance_accounts
                WHERE connection_id = $1
            )
        """

        async with self.pool.acquire() as db:
            await db.execute(
                query,
                connection_id,
            )