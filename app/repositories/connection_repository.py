from abc import ABC, abstractmethod

import asyncpg

from app.connections.models import (
    BankConnection,
    ConnectionStatus,
)


class ConnectionRepository(ABC):

    @abstractmethod
    async def create(
        self,
        connection: BankConnection,
    ) -> BankConnection:
        pass

    @abstractmethod
    async def find_by_id(
        self,
        connection_id: str,
    ) -> BankConnection | None:
        pass

    @abstractmethod
    async def find_by_id_and_user_id(
        self,
        connection_id: str,
        user_id: str,
    ) -> BankConnection | None:
        pass

    @abstractmethod
    async def find_by_user_id(
        self,
        user_id: str,
    ) -> list[BankConnection]:
        pass

    @abstractmethod
    async def update_last_synced_at(
        self,
        connection_id: str,
    ) -> None:
        pass

    @abstractmethod
    async def update_status(
        self,
        connection_id: str,
        status: ConnectionStatus,
    ) -> None:
        """Move a connection to a new lifecycle state.

        Called only after the provider has confirmed the transition, so the
        stored status never runs ahead of what actually happened upstream.
        """
        pass

    @abstractmethod
    async def get_last_synced_at(
        self,
        connection_id: str,
    ):
        pass

class PostgreSQLConnectionRepository(ConnectionRepository):

    def __init__(
        self,
        pool: asyncpg.Pool,
    ):
        self.pool = pool

    async def create(
        self,
        connection: BankConnection,
    ) -> BankConnection:

        query = """
            INSERT INTO open_finance_connections (
                id,
                user_id,
                provider,
                external_id,
                status
            )
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (provider, external_id)
            DO UPDATE SET
                status = EXCLUDED.status,
                updated_at = CURRENT_TIMESTAMP
            RETURNING
                id,
                user_id,
                provider,
                external_id,
                status,
                last_synced_at
        """

        async with self.pool.acquire() as db:
            row = await db.fetchrow(
                query,
                connection.id,
                connection.user_id,
                connection.provider,
                connection.external_id,
                connection.status.value,
            )

        return BankConnection(
            id=str(row["id"]),
            user_id=str(row["user_id"]),
            provider=row["provider"],
            external_id=row["external_id"],
            status=ConnectionStatus(row["status"]),
            last_synced_at=row["last_synced_at"],
        )

    async def find_by_id(
        self,
        connection_id: str,
    ) -> BankConnection | None:

        query = """
            SELECT
                id,
                user_id,
                provider,
                external_id,
                status,
                last_synced_at
            FROM open_finance_connections
            WHERE id = $1
        """

        async with self.pool.acquire() as db:
            row = await db.fetchrow(
                query,
                connection_id,
            )

        if not row:
            return None

        return BankConnection(
            id=str(row["id"]),
            user_id=str(row["user_id"]),
            provider=row["provider"],
            external_id=row["external_id"],
            status=ConnectionStatus(row["status"]),
            last_synced_at=row["last_synced_at"],
        )

    async def update_last_synced_at(
        self,
        connection_id: str,
    ) -> None:

        query = """
            UPDATE open_finance_connections
            SET
                last_synced_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        """

        async with self.pool.acquire() as db:
            await db.execute(
                query,
                connection_id,
            )    

    async def update_status(
        self,
        connection_id: str,
        status: ConnectionStatus,
    ) -> None:

        query = """
            UPDATE open_finance_connections
            SET
                status = $2,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        """

        async with self.pool.acquire() as db:
            await db.execute(
                query,
                connection_id,
                status.value,
            )

    async def get_last_synced_at(
        self,
        connection_id: str,
    ):

        query = """
            SELECT last_synced_at
            FROM open_finance_connections
            WHERE id = $1
        """

        async with self.pool.acquire() as db:
            row = await db.fetchrow(
                query,
                connection_id,
            )

        if not row:
            return None

        return row["last_synced_at"]       

    async def find_by_id_and_user_id(
        self,
        connection_id: str,
        user_id: str,
    ) -> BankConnection | None:
        query = """
            SELECT
                id,
                user_id,
                provider,
                external_id,
                status,
                last_synced_at
            FROM open_finance_connections
            WHERE id = $1
            AND user_id = $2
        """

        async with self.pool.acquire() as db:
            row = await db.fetchrow(
                query,
                connection_id,
                user_id,
            )

        if not row:
            return None

        return BankConnection(
            id=str(row["id"]),
            user_id=str(row["user_id"]),
            provider=row["provider"],
            external_id=row["external_id"],
            status=ConnectionStatus(row["status"]),
            last_synced_at=row["last_synced_at"],
        ) 

    async def find_by_user_id(
        self,
        user_id: str,
    ) -> list[BankConnection]:

        query = """
            SELECT
                id,
                user_id,
                provider,
                external_id,
                status,
                last_synced_at
            FROM open_finance_connections
            WHERE user_id = $1
            ORDER BY created_at DESC
        """

        async with self.pool.acquire() as db:
            rows = await db.fetch(query, user_id)

        return [
            BankConnection(
                id=str(row["id"]),
                user_id=str(row["user_id"]),
                provider=row["provider"],
                external_id=row["external_id"],
                status=ConnectionStatus(row["status"]),
                last_synced_at=row["last_synced_at"],
            )
            for row in rows
        ]

    