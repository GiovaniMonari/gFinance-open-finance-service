import os

from dotenv import load_dotenv

from app.connections.providers.base import OpenFinanceProvider
from app.connections.providers.mock import MockOpenFinanceProvider
from app.connections.providers.pluggy_provider import PluggyOpenFinanceProvider

load_dotenv()


def get_open_finance_provider() -> OpenFinanceProvider:
    provider = os.getenv(
        "OPEN_FINANCE_PROVIDER",
        "mock",
    )

    if provider == "mock":
        return MockOpenFinanceProvider()

    if provider == "pluggy":
        return PluggyOpenFinanceProvider()

    raise ValueError(
        f"Open Finance provider não suportado: {provider}"
    )