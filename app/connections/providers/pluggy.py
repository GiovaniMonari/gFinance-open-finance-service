import os

import httpx
from dotenv import load_dotenv

from app.connections.exceptions import (
    ProviderAuthError,
    ProviderNotFoundError,
    ProviderUnavailableError,
)

load_dotenv()


class PluggyClient:
    def __init__(self):
        self.base_url = os.getenv(
            "PLUGGY_BASE_URL",
            "https://api.pluggy.ai",
        )

        self.client_id = os.getenv("PLUGGY_CLIENT_ID")
        self.client_secret = os.getenv("PLUGGY_CLIENT_SECRET")

    async def authenticate(self) -> str:
        if not self.client_id or not self.client_secret:
            raise RuntimeError(
                "PLUGGY_CLIENT_ID e PLUGGY_CLIENT_SECRET "
                "não configurados"
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth",
                json={
                    "clientId": self.client_id,
                    "clientSecret": self.client_secret,
                },
            )

        response.raise_for_status()

        data = response.json()

        return data["apiKey"]

    async def create_connect_token(
        self,
        client_user_id: str,
    ) -> str:
        api_key = await self.authenticate()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/connect_token",
                headers={
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "options": {
                        "clientUserId": client_user_id,
                        "avoidDuplicates": True,
                    }
                },
            )

        response.raise_for_status()

        data = response.json()

        return data["accessToken"]

    async def get_item(self, item_id: str) -> dict:
        api_key = await self.authenticate()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/items/{item_id}",
                headers={
                    "X-API-KEY": api_key,
                },
            )

        # The item is gone upstream — revoked from another device, dropped by
        # Pluggy when a connector was deprecated, or closed by the user at the
        # bank. The consent no longer exists; that is a missing connection, not
        # a 500 that reads like a fault in this service.
        if response.status_code == 404:
            raise ProviderNotFoundError()

        response.raise_for_status()

        return response.json()

    async def delete_item(self, item_id: str) -> bool:
        """Revoke the connection at Pluggy.

        ``DELETE /items/{id}`` is the documented way to sever the link: the
        item is marked deleted, the stored credentials are wiped, the Open
        Finance consent is revoked and any OAuth authorization expires.
        Pluggy then purges the item's accounts and transactions, which is why
        flipping our own record to "disconnected" without this call would
        leave the user still sharing their data with the aggregator.

        Returns ``False`` when Pluggy has no record of the item, meaning the
        consent was already revoked.
        """
        try:
            api_key = await self.authenticate()
        except RuntimeError as error:
            # Our own credentials are missing — an auth fault, not an outage.
            raise ProviderAuthError() from error
        except (httpx.HTTPError, KeyError) as error:
            # Pluggy could not be reached, or answered without a usable key.
            raise ProviderUnavailableError() from error

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/items/{item_id}",
                    headers={
                        "X-API-KEY": api_key,
                    },
                )
        except httpx.HTTPError as error:
            raise ProviderUnavailableError() from error

        # Gone upstream: the revocation the user asked for is already true.
        if response.status_code == 404:
            return False

        if response.status_code in (401, 403):
            raise ProviderAuthError()

        if response.status_code >= 400:
            raise ProviderUnavailableError()

        return True

    async def get_accounts(self, item_id: str) -> list[dict]:
        api_key = await self.authenticate()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/accounts",
                headers={
                    "X-API-KEY": api_key,
                },
                params={
                    "itemId": item_id,
                },
            )

        response.raise_for_status()

        data = response.json()

        print("PLUGGY ACCOUNTS:", data)

        return data.get("results", [])   

    async def get_transactions(
        self,
        account_id: str,
        since=None,
    ) -> list[dict]:
        api_key = await self.authenticate()

        params = {
            "accountId": account_id,
        }

        if since:
            params["dateFrom"] = since

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v2/transactions",
                headers={"X-API-KEY": api_key},
                params=params,
            )

        print(
            "PLUGGY TRANSACTIONS RESPONSE:",
            response.text,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("results", [])