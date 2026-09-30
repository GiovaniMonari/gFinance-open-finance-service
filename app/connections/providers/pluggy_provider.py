from app.connections.models import BankConnection
from app.connections.providers.base import OpenFinanceProvider
from app.connections.providers.pluggy import PluggyClient
from app.repositories.connection_repository import ConnectionRepository
from app.translations import (
    translate_account,
    translate_transaction_payload,
)


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
        item_id: str | None = None,
    ):
        if not item_id:
            raise ValueError(
                "item_id é obrigatório para criar uma conexão "
                "no provedor Pluggy"
            )

        item = await self.client.get_item(item_id)

        return {
            "external_id": item["id"],
            "status": "connected",
        }

    async def disconnect(
        self,
        connection: BankConnection,
    ) -> bool:
        """Revoke the Pluggy item that backs this connection.

        Everything happens at the provider first; the caller only updates our
        record once this returns, so local state can never claim a
        disconnection Pluggy did not confirm.
        """
        return await self.client.delete_item(
            connection.external_id,
        )

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

        item = await self.client.get_item(
            connection.external_id
        )

        bank_name = (
            item.get("institution", {}) or {}
        ).get("name")

        accounts = await self.client.get_accounts(
            connection.external_id
        )

        # English labels become pt-BR here, at the single point where a
        # Pluggy payload turns into something the app will show a person.
        return [
            translate_account(
                {
                    "id": account.get("id"),
                    "type": account.get("type"),
                    "subtype": account.get("subtype"),
                    "name": account.get("name"),
                    "balance": account.get("balance"),
                    "currency_code": account.get("currencyCode"),
                    "marketing_name": account.get("marketingName"),
                    "bank": {
                        "name": bank_name,
                        "transfer_number": (
                            account.get("bankData", {}) or {}
                        ).get("transferNumber"),
                    }
                    if account.get("type") == "BANK"
                    else None,
                    "credit": {
                        "brand": (
                            account.get("creditData", {}) or {}
                        ).get("brand"),
                        "available_credit_limit": (
                            account.get("creditData", {}) or {}
                        ).get("availableCreditLimit"),
                        "credit_limit": (
                            account.get("creditData", {}) or {}
                        ).get("creditLimit"),
                        "minimum_payment": (
                            account.get("creditData", {}) or {}
                        ).get("minimumPayment"),
                        "balance_due_date": (
                            account.get("creditData", {}) or {}
                        ).get("balanceDueDate"),
                        "status": (
                            account.get("creditData", {}) or {}
                        ).get("status"),
                    }
                    if account.get("creditData")
                    else None,
                }
            )
            for account in accounts
        ]

    async def get_transactions(
        self,
        account_id: str,
        since=None,
    ):
        transactions = await self.client.get_transactions(
            account_id=account_id,
            since=since,
        )

        return [
            translate_transaction_payload(transaction)
            for transaction in transactions
        ]
