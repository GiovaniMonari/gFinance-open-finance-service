from app.connections.providers.base import OpenFinanceProvider
from app.connections.providers.pluggy import PluggyClient
from app.repositories.connection_repository import ConnectionRepository


class PluggyOpenFinanceProvider(OpenFinanceProvider):

    def __init__(
        self,
        connection_repository: ConnectionRepository,
    ):
        self.client = PluggyClient()
        self.connection_repository = connection_repository

    @property
    def name(self) -> str:
        return "pluggy"

    async def create_connection(
        self,
        user_id: str,
        item_id: str,
    ):
        item = await self.client.get_item(item_id)

        return {
            "external_id": item["id"],
            "status": "connected",
        }

    async def get_accounts(
        self,
        connection_id: str,
    ):
        connection = await self.connection_repository.find_by_id(
            connection_id
        )

        if not connection:
            raise ValueError(
                f"Conexão não encontrada: {connection_id}"
            )

        return await self.client.get_accounts(
            connection.external_id
        )

    async def get_transactions(
        self,
        account_id: str,
        since=None,
    ):
        raise NotImplementedError