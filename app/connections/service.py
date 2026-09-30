import uuid

from app.connections.exceptions import (
    ConnectionAlreadyDisconnectedError,
    ConnectionNotFoundError,
)
from app.connections.models import (
    BankConnection,
    ConnectionStatus,
)
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

    async def disconnect_connection(
        self,
        user_id: str,
        connection_id: str,
    ) -> BankConnection:
        """Revoke a single user's connection, end to end.

        The row is looked up by both ids at once, so a connection owned by
        somebody else is answered exactly like one that never existed — the
        caller cannot probe for ids that are not theirs.

        Order matters: the provider is asked to revoke first and only a
        confirmed revocation flips our own record. If Pluggy fails, the stored
        status stays "connected", which is still the truth, and the user can
        retry instead of being left believing their data stopped flowing.
        """
        connection = await self.repository.find_by_id_and_user_id(
            connection_id,
            user_id,
        )

        if connection is None:
            raise ConnectionNotFoundError()

        if connection.status == ConnectionStatus.DISCONNECTED:
            raise ConnectionAlreadyDisconnectedError()

        # Answers `False` when Pluggy had already forgotten the item, which
        # is the outcome the user asked for, not an error.
        await self.provider.disconnect(connection)

        await self.repository.update_status(
            connection.id,
            ConnectionStatus.DISCONNECTED,
        )

        return connection.model_copy(
            update={"status": ConnectionStatus.DISCONNECTED},
        )
