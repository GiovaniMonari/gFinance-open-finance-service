import os

from dotenv import load_dotenv

from app.connections.providers.base import OpenFinanceProvider
from app.connections.providers.mock import MockOpenFinanceProvider
from app.connections.providers.pluggy_provider import PluggyOpenFinanceProvider
from app.repositories.connection_repository import ConnectionRepository

load_dotenv()


def get_open_finance_provider(
    connection_repository: ConnectionRepository | None = None,
) -> OpenFinanceProvider:

    provider = os.getenv(
        "OPEN_FINANCE_PROVIDER",
        "mock",
    )

    if provider == "mock":
        return MockOpenFinanceProvider()

    if provider == "pluggy":
        if connection_repository is None:
            raise ValueError(
                "ConnectionRepository é obrigatório para o provider Pluggy"
            )

        return PluggyOpenFinanceProvider(
            connection_repository=connection_repository,
        )

    raise ValueError(
        f"Open Finance provider não suportado: {provider}"
    )