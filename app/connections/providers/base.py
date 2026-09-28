from abc import ABC, abstractmethod


class OpenFinanceProvider(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def create_connection(self, user_id: str):
        pass

    @abstractmethod
    async def get_accounts(self, connection_id: str):
        pass

    @abstractmethod
    async def get_transactions(
        self,
        account_id: str,
        since=None,
    ):
        pass