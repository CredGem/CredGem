from typing import Optional

from httpx import AsyncClient

from credgem.api.wallets import WalletsAPI
from credgem.api.transactions import TransactionsAPI
from credgem.api.credit_types import CreditTypesAPI
from credgem.api.insights import InsightsAPI


class CredGemClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: float = 10.0,
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = AsyncClient(
            base_url=self._base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        # Initialize API resources
        self.wallets = WalletsAPI(self._client)
        self.transactions = TransactionsAPI(self._client)
        self.credit_types = CreditTypesAPI(self._client)
        self.insights = InsightsAPI(self._client)

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close() 