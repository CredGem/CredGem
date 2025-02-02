from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, AsyncGenerator
from decimal import Decimal
import httpx

from .api.wallets import WalletsAPI
from .api.credit_types import CreditTypesAPI
from .api.transactions import TransactionsAPI
from .models import TransactionResponse


class CredGemClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.credgem.com/api/v1",
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        # Initialize API interfaces
        self.wallets = WalletsAPI(self._client)
        self.credit_types = CreditTypesAPI(self._client)
        self.transactions = TransactionsAPI(self._client)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    @asynccontextmanager
    async def draw_credits(
        self,
        wallet_id: str,
        credit_type_id: str,
        amount: float,
        description: str,
        issuer: str,
        external_transaction_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        skip_hold: bool = False,
    ) -> AsyncGenerator[None, None]:
        """Context manager for drawing credits from a wallet.
        
        If skip_hold is True, skips the hold step and directly debits the credits.
        Otherwise, places a hold on the credits when entering the context and either
        debits or releases them when exiting.
        """
        hold_transaction = None
        try:
            if not skip_hold:
                # Place hold on credits
                hold_transaction = await self.transactions.hold(
                    wallet_id=wallet_id,
                    credit_type_id=credit_type_id,
                    amount=amount,
                    description=description,
                    context=context,
                )

            class DrawContext:
                async def debit(self) -> TransactionResponse:
                    if skip_hold:
                        # Direct debit without hold
                        return await self.transactions.debit(
                            wallet_id=wallet_id,
                            credit_type_id=credit_type_id,
                            amount=amount,
                            description=description,
                            context=context,
                        )
                    else:
                        # Debit with existing hold
                        return await self.transactions.debit(
                            wallet_id=wallet_id,
                            credit_type_id=credit_type_id,
                            amount=amount,
                            description=description,
                            context=context,
                        )

            yield DrawContext()

            if hold_transaction and not skip_hold:
                # Release hold if no debit was performed
                await self.transactions.release(hold_transaction.id)

        except Exception as e:
            if hold_transaction and not skip_hold:
                # Release hold on any error
                await self.transactions.release(hold_transaction.id)
            raise e 