import os

import httpx
from dotenv import load_dotenv

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

        response.raise_for_status()

        return response.json()

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

        return data.get("results", []) 

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

        return data.get("results", [])   