import uuid

from app.connections.exceptions import (
    ConnectionAlreadyDisconnectedError,
    ConnectionNotFoundError,
    OpenFinanceError,
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

        external_id = provider_connection["external_id"]

        connection = BankConnection(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider=self.provider.name,
            external_id=external_id,
            status=provider_connection["status"],
        )

        saved = await self.repository.create(connection)

        # One account holds one link. The new row lands first, so a failure
        # to store it leaves the link the user already had untouched; only
        # once it is safe does anything else this user still has open go
        # down, so a second row can never be left behind to be discovered
        # later as a connection nobody remembers making.
        await self.retire_other_connections(
            user_id,
            keep_external_id=external_id,
        )

        return saved

    async def active_connections(
        self,
        user_id: str,
    ) -> list[BankConnection]:
        """Every link this user still holds, read straight from the table.

        The database is the only authority on what is connected: there is no
        cache, no mirror and no job that writes this status, so whatever is
        stored here is what every later read will answer.
        """
        connections = await self.repository.find_by_user_id(user_id)

        return [
            connection
            for connection in connections
            if connection.status != ConnectionStatus.DISCONNECTED
        ]

    async def revoke(
        self,
        connection: BankConnection,
    ) -> BankConnection:
        """Take one link down at the provider, then record that it is down.

        Order matters: the provider is asked first and only a confirmed
        revocation flips our own record. If Pluggy fails, the stored status
        stays "connected", which is still the truth, and the user can retry
        instead of being left believing their data stopped flowing.

        ``disconnect`` answers ``False`` when Pluggy had already forgotten
        the item, which is the outcome the user asked for, not an error.
        """
        await self.provider.disconnect(connection)

        await self.repository.update_status(
            connection.id,
            ConnectionStatus.DISCONNECTED,
        )

        return connection.model_copy(
            update={"status": ConnectionStatus.DISCONNECTED},
        )

    async def retire_other_connections(
        self,
        user_id: str,
        keep_external_id: str | None = None,
    ) -> None:
        """Close every link of this user except the one being kept.

        Best effort on purpose: a link that could not be revoked upstream is
        left alone and stays "connected", because that is what is true. The
        row being adopted is never touched, so reconnecting to the item the
        user already owns does not revoke the very connection it is keeping.
        """
        for connection in await self.active_connections(user_id):
            if keep_external_id and connection.external_id == keep_external_id:
                continue

            try:
                await self.revoke(connection)
            except OpenFinanceError as error:
                print(
                    "Não foi possível aposentar a conexão "
                    f"{connection.id} do usuário {user_id}: "
                    f"{error.detail}"
                )

    async def disconnect_connection(
        self,
        user_id: str,
        connection_id: str,
    ) -> BankConnection:
        """Revoke the user's connection, end to end.

        The row is looked up by both ids at once, so a connection owned by
        somebody else is answered exactly like one that never existed — the
        caller cannot probe for ids that are not theirs. Every other row
        considered afterwards is selected by the same user id, so a second
        user's links can never be swept up in this call.

        One account holds one link, but nothing in the table enforces that:
        each connect that arrives carrying a new provider item inserts its
        own row. Flipping only the row named by the caller would leave those
        siblings untouched, and the next read would offer the user a
        connection they had just severed. So the whole set goes down
        together, and "disconnected" means the account has none left.
        """
        connection = await self.repository.find_by_id_and_user_id(
            connection_id,
            user_id,
        )

        if connection is None:
            raise ConnectionNotFoundError()

        active = await self.active_connections(user_id)

        if not active:
            raise ConnectionAlreadyDisconnectedError()

        for link in active:
            await self.revoke(link)

        return connection.model_copy(
            update={"status": ConnectionStatus.DISCONNECTED},
        )
