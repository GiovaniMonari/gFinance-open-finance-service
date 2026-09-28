import uuid

from app.connections.models import BankConnection
from app.connections.providers.base import OpenFinanceProvider
from app.repositories.connection_repository import ConnectionRepository


class ConnectionService:

    def __init__(
        self,
        provider: OpenFinanceProvider,
        repository: ConnectionRepository,
    ):
        self.provider = provider
        self.repository = repository

    async def create_connection(
        self,
        user_id: str,
        item_id: str | None = None,
    ) -> BankConnection:
        if item_id:
            provider_connection = await self.provider.create_connection(
                user_id,
                item_id,
            )
        else:
            provider_connection = await self.provider.create_connection(
                user_id,
            )

        connection = BankConnection(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider=self.provider.name,
            external_id=provider_connection["external_id"],
            status=provider_connection["status"],
        )

        return await self.repository.create(connection)