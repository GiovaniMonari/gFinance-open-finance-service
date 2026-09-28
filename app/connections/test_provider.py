import asyncio

from app.connections.providers.mock import MockOpenFinanceProvider


async def main():
    provider = MockOpenFinanceProvider()

    connection = await provider.create_connection("user-001")

    print("Connection:")
    print(connection)

    accounts = await provider.get_accounts(
        connection["external_id"]
    )

    print("\nAccounts:")
    print(accounts)

    transactions = await provider.get_transactions(
        accounts[0]["external_id"]
    )

    print("\nTransactions:")
    print(transactions)


asyncio.run(main())