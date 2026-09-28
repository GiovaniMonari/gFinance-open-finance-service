from abc import ABC, abstractmethod

import asyncpg

from app.synchronization.models import (
    SynchronizationJob,
    SyncStatus,
)


class SynchronizationRepository(ABC):

    @abstractmethod
    async def create(
        self,
        job: SynchronizationJob,
    ) -> SynchronizationJob:
        pass

    @abstractmethod
    async def update_status(
        self,
        job_id: str,
        status: SyncStatus,
        accounts_count: int = 0,
        transactions_count: int = 0,
        error: str | None = None,
    ) -> None:
        pass

    @abstractmethod
    async def find_by_id(
        self,
        job_id: str,
    ) -> SynchronizationJob | None:
        pass

    @abstractmethod
    async def find_active_by_connection_id(
        self,
        connection_id: str,
    ) -> SynchronizationJob | None:
        pass

    @abstractmethod
    async def find_by_connection_id(
        self,
        connection_id: str,
    ) -> list[SynchronizationJob]:
        pass

    @abstractmethod
    async def find_by_id_and_user_id(
        self,
        job_id: str,
        user_id: str,
    ) -> SynchronizationJob | None:
        pass

class PostgreSQLSynchronizationRepository(
    SynchronizationRepository
):

    def __init__(
        self,
        pool: asyncpg.Pool,
    ):
        self.pool = pool

    async def create(
        self,
        job: SynchronizationJob,
    ) -> SynchronizationJob:

        query = """
            INSERT INTO open_finance_sync_jobs (
                id,
                connection_id,
                user_id,
                status,
                accounts_count,
                transactions_count,
                error
            )
            VALUES (
                $1, $2, $3, $4, $5, $6, $7
            )
        """

        async with self.pool.acquire() as db:
            await db.execute(
                query,
                job.id,
                job.connection_id,
                job.user_id,
                job.status.value,
                job.accounts_count,
                job.transactions_count,
                job.error,
            )

        return job

    async def update_status(
        self,
        job_id: str,
        status: SyncStatus,
        accounts_count: int = 0,
        transactions_count: int = 0,
        error: str | None = None,
    ) -> None:

        query = """
            UPDATE open_finance_sync_jobs
            SET
                status = $2,
                accounts_count = $3,
                transactions_count = $4,
                error = $5,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        """

        async with self.pool.acquire() as db:
            await db.execute(
                query,
                job_id,
                status.value,
                accounts_count,
                transactions_count,
                error,
            )

    async def find_by_id(
        self,
        job_id: str,
    ) -> SynchronizationJob | None:

        query = """
            SELECT
                id,
                connection_id,
                user_id,
                status,
                accounts_count,
                transactions_count,
                error
            FROM open_finance_sync_jobs
            WHERE id = $1
        """

        async with self.pool.acquire() as db:
            row = await db.fetchrow(
                query,
                job_id,
            )

        if not row:
            return None

        return SynchronizationJob(
            id=str(row["id"]),
            connection_id=str(row["connection_id"]),
            user_id=str(row["user_id"]),
            status=SyncStatus(row["status"]),
            accounts_count=row["accounts_count"],
            transactions_count=row["transactions_count"],
            error=row["error"],
        )

    async def find_by_id_and_user_id(
        self,
        job_id: str,
        user_id: str,
    ) -> SynchronizationJob | None:
        query = """
            SELECT
                id,
                connection_id,
                user_id,
                status,
                accounts_count,
                transactions_count,
                error
            FROM open_finance_sync_jobs
            WHERE id = $1
            AND user_id = $2
        """

        async with self.pool.acquire() as db:
            row = await db.fetchrow(
                query,
                job_id,
                user_id,
            )

        if not row:
            return None

        return SynchronizationJob(
            id=str(row["id"]),
            connection_id=str(row["connection_id"]),
            user_id=str(row["user_id"]),
            status=SyncStatus(row["status"]),
            accounts_count=row["accounts_count"],
            transactions_count=row["transactions_count"],
            error=row["error"],
        )

    async def find_active_by_connection_id(
        self,
        connection_id: str,
    ) -> SynchronizationJob | None:

        query = """
            SELECT
                id,
                connection_id,
                user_id,
                status,
                accounts_count,
                transactions_count,
                error
            FROM open_finance_sync_jobs
            WHERE connection_id = $1
            AND status IN ('pending', 'processing')
            ORDER BY created_at DESC
            LIMIT 1
        """

        async with self.pool.acquire() as db:
            row = await db.fetchrow(
                query,
                connection_id,
            )

        if not row:
            return None

        return SynchronizationJob(
            id=str(row["id"]),
            connection_id=str(row["connection_id"]),
            user_id=str(row["user_id"]),
            status=SyncStatus(row["status"]),
            accounts_count=row["accounts_count"],
            transactions_count=row["transactions_count"],
            error=row["error"],
        )    
    
    async def find_by_connection_id(
        self,
        connection_id: str,
    ) -> list[SynchronizationJob]:
        query = """
            SELECT
                id,
                connection_id,
                user_id,
                status,
                accounts_count,
                transactions_count,
                error
            FROM open_finance_sync_jobs
            WHERE connection_id = $1
            ORDER BY created_at DESC
        """

        async with self.pool.acquire() as db:
            rows = await db.fetch(query, connection_id)

        return [
            SynchronizationJob(
                id=str(row["id"]),
                connection_id=str(row["connection_id"]),
                user_id=str(row["user_id"]),
                status=SyncStatus(row["status"]),
                accounts_count=row["accounts_count"],
                transactions_count=row["transactions_count"],
                error=row["error"],
            )
            for row in rows
        ]