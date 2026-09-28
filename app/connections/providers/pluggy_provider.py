from app.connections.providers.base import OpenFinanceProvider
from app.connections.providers.pluggy import PluggyClient


class PluggyOpenFinanceProvider(OpenFinanceProvider):

    def __init__(self):
        self.client = PluggyClient()

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

    async def get_accounts(self, connection_id: str):
        raise NotImplementedError

    async def get_transactions(
        self,
        account_id: str,
        since=None,
    ):
        raise NotImplementedError