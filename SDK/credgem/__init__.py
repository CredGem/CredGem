from typing import Optional
from decimal import Decimal

from httpx import AsyncClient

from credgem.api.wallets import WalletsAPI
from credgem.api.transactions import TransactionsAPI
from credgem.api.credit_types import CreditTypesAPI
from credgem.api.insights import InsightsAPI
from credgem.contexts import DrawCredits


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

    def draw_credits(
        self,
        wallet_id: str,
        credit_type_id: str,
        amount: Decimal,
        description: str,
        issuer: str,
        transaction_id: Optional[str] = None,
        context: Optional[dict] = None,
        skip_hold: bool = False,
    ) -> DrawCredits:
        """
        Create a DrawCredits context manager for handling credit operations.
        
        This provides a safe way to handle credit operations with automatic
        cleanup in case of errors. It will:
        1. Hold the specified amount of credits
        2. Allow you to process your operation
        3. You must explicitly call debit() or release() to complete the operation
        
        Example:
            async with client.draw_credits(
                wallet_id="wallet_123",
                credit_type_id="POINTS",
                amount=Decimal("10.00"),
                description="Purchase credits",
                issuer="store_app",
                context={"order_id": "order_123"}
            ) as draw:
                # Process your operation
                result = await process_order()
                if result.success:
                    # Debit with optional different amount and additional context
                    await draw.debit(
                        amount=Decimal("9.99"),
                        context={"status": "completed"}
                    )
                else:
                    # Explicitly release the hold with context
                    await draw.release(
                        context={"status": "failed"}
                    )
        """
        return DrawCredits(
            client=self.transactions,
            wallet_id=wallet_id,
            credit_type_id=credit_type_id,
            amount=amount,
            description=description,
            issuer=issuer,
            transaction_id=transaction_id,
            context=context,
            skip_hold=skip_hold,
        )

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close() 