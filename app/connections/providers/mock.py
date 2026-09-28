from app.connections.providers.base import OpenFinanceProvider
from datetime import datetime

class MockOpenFinanceProvider(OpenFinanceProvider):

    @property
    def name(self) -> str:
        return "mock-provider"

    async def create_connection(self, user_id: str):
        return {
            "external_id": f"mock-connection-{user_id}",
            "status": "connected",
        }

    async def get_accounts(self, connection_id: str):
        return [
            {
                "external_id": "mock-account-001",
                "name": "Conta Corrente",
                "bank_name": "Banco Mock",
                "account_type": "checking",
                "balance": 2500.00,
            }
        ]

    async def get_transactions(
        self,
        account_id: str,
        since=None,
    ):
        transactions = [
            {
                "external_id": "mock-transaction-001",
                "amount": 150.90,
                "description": "Supermercado XYZ",
                "date": "2026-09-26",
                "type": "expense",
            },
            {
                "external_id": "mock-transaction-002",
                "amount": 3500.00,
                "description": "Salário",
                "date": "2026-09-25",
                "type": "income",
            },
        ]

        if since is None:
            return transactions

        since_date = since.date()

        return [
            transaction
            for transaction in transactions
            if datetime.strptime(
                transaction["date"],
                "%Y-%m-%d",
            ).date() >= since_date
        ]