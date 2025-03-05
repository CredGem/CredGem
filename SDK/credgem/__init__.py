from typing import Dict, Optional

import httpx

from .api.credit_types import CreditTypesAPI
from .api.insights import InsightsAPI
from .api.transactions import TransactionsAPI
from .api.wallets import WalletsAPI
from .contexts import DrawCredits


class CredGemClient:
    """Main client for interacting with the CredGem API."""

    def __init__(self, api_key: str, base_url: str):
        """Initialize the client.

        Args:
            api_key: The API key for authentication
            base_url: The base URL of the API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        """Set up the HTTP client and API clients."""
        self.http_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            follow_redirects=True,
        )
        # Initialize API clients
        self.wallets = WalletsAPI(self.http_client)
        self.transactions = TransactionsAPI(self.http_client)
        self.credit_types = CreditTypesAPI(self.http_client)
        self.insights = InsightsAPI(self.http_client)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up the HTTP client."""
        if self.http_client:
            await self.http_client.aclose()

    def draw_credits(
        self,
        wallet_id: str,
        credit_type_id: str,
        amount: float,
        description: str = "",
        issuer: str = "",
        external_id: Optional[str] = None,
        context: Optional[Dict] = None,
        skip_hold: bool = False,
    ) -> DrawCredits:
        """Create a DrawCredits context manager for safe credit operations.

        Args:
            wallet_id: The ID of the wallet to draw credits from
            credit_type_id: The type of credits to draw
            amount: The amount of credits to hold/debit
            description: A description of the transaction
            issuer: The issuer of the transaction
            external_id: Optional transaction ID for idempotency
            context: Optional context data for the transaction
            skip_hold: Whether to skip the hold step and debit directly

        Returns:
            A DrawCredits context manager
        """
        return DrawCredits(
            client=self,
            wallet_id=wallet_id,
            credit_type_id=credit_type_id,
            amount=amount,
            description=description,
            issuer=issuer,
            external_id=external_id,
            context=context,
            skip_hold=skip_hold,
        )
