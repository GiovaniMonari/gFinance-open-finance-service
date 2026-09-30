from abc import ABC, abstractmethod

from app.connections.models import BankConnection


class OpenFinanceProvider(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def create_connection(
        self,
        user_id: str,
        item_id: str | None = None,
    ):
        pass

    @abstractmethod
    async def disconnect(
        self,
        connection: BankConnection,
    ) -> bool:
        """Revoke the connection on the provider's side.

        Returns ``True`` when the provider confirmed the revocation and
        ``False`` when it had already forgotten the connection, so callers can
        report an idempotent outcome instead of inventing an error for a state
        that is already the one the user asked for.

        Implementations raise ``ProviderAuthError`` or
        ``ProviderUnavailableError`` when the provider could not be reached or
        refused us.
        """

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
