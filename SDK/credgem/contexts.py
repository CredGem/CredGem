import uuid
import logging
from typing import Optional, Dict, Any, Tuple, Awaitable
from decimal import Decimal

from httpx import HTTPStatusError, HTTPError

from credgem.api.base import BaseAPI
from credgem.api.transactions import TransactionResponse
from credgem.exceptions import InsufficientCreditsError

logger = logging.getLogger(__name__)


class DrawCredits:
    """Context manager for drawing credits from a wallet.
    
    This context manager handles the lifecycle of a credit transaction, including:
    - Creating a hold on credits (optional)
    - Debiting credits
    - Releasing held credits if not debited
    - Handling errors and cleanup
    """
    
    def __init__(
        self,
        client,
        wallet_id: str,
        credit_type_id: str,
        amount: Optional[Decimal] = None,
        description: str = "",
        issuer: str = "",
        transaction_id: Optional[str] = None,
        context: Optional[Dict] = None,
        skip_hold: bool = False
    ):
        """Initialize the DrawCredits context.
        
        Args:
            client: The CredGemClient instance
            wallet_id: The ID of the wallet to draw credits from
            credit_type_id: The type of credits to draw
            amount: The amount of credits to hold/debit (optional if skip_hold=True)
            description: A description of the transaction
            issuer: The issuer of the transaction
            transaction_id: Optional transaction ID for idempotency
            context: Optional context data for the transaction
            skip_hold: Whether to skip the hold step and debit directly
        """
        self.client = client
        self.wallet_id = wallet_id
        self.credit_type_id = credit_type_id
        self.amount = amount
        self.description = description
        self.issuer = issuer
        self.transaction_id = transaction_id
        self.context = context or {}
        self.skip_hold = skip_hold
        
        self.hold_id = None
        self.debit_amount = None
    
    async def _handle_api_call(self, coro: Awaitable[TransactionResponse]) -> Tuple[bool, Optional[TransactionResponse]]:
        """Handle API call with proper error handling."""
        try:
            response = await coro
            print("debug response", response)
            return True, response
        except HTTPError as e:
            print("debug error response", e.response.status_code, e.response.json())
            if e.response.status_code == 409:
                # 409 means the operation was already completed
                # Just return success without the response since we get an error message
                return True, None
            elif e.response.status_code == 422:
                # 422 means insufficient credits
                raise InsufficientCreditsError("Insufficient credits available")
            else:
                raise
    
    async def hold(self):
        """Create a hold on the credits."""
        if self.skip_hold:
            return
        
        if self.hold_id:
            return
        
        if not self.amount:
            raise ValueError("Amount is required for hold operation")
        
        logger.info(
            f"Creating hold for {self.amount} credits for wallet {self.wallet_id}"
        )
        success, response = await self._handle_api_call(
            self.client.hold(
                wallet_id=self.wallet_id,
                amount=self.amount,
                credit_type_id=self.credit_type_id,
                description=self.description,
                issuer=self.issuer,
                transaction_id=self.transaction_id,
                idempotency_key=f"hold_{self.transaction_id}",
                context=self.context
            )
        )
        if success and response:
            self.hold_id = response.id
    
    async def debit(self, amount: Optional[Decimal] = None, context: Optional[Dict] = None):
        """Debit credits from the wallet.
        
        Args:
            amount: Optional amount to debit. If not provided, uses the hold amount.
            context: Optional context to override the initial context.
        """
        if not self.skip_hold and not amount and not self.amount:
            raise ValueError("Amount is required for debit operation")
        
        debit_amount = amount or self.amount
        debit_context = {**self.context, **(context or {})}
        
        logger.info(
            f"Debiting {debit_amount} credits from wallet {self.wallet_id}"
        )
        success, response = await self._handle_api_call(
            self.client.debit(
                wallet_id=self.wallet_id,
                amount=debit_amount,
                credit_type_id=self.credit_type_id,
                description=self.description,
                issuer=self.issuer,
                hold_transaction_id=self.hold_id,
                transaction_id=self.transaction_id,
                idempotency_key=f"debit_{self.transaction_id}",
                context=debit_context
            )
        )
        if success:
            self.debit_amount = debit_amount
    
    async def release(self, context: Optional[Dict] = None):
        """Release held credits.
        
        Args:
            context: Optional context to override the initial context.
        """
        if not self.hold_id:
            return
        
        release_context = {**self.context, **(context or {})}
        
        logger.info(
            f"Releasing hold {self.hold_id} for wallet {self.wallet_id}"
        )
        success, _ = await self._handle_api_call(
            self.client.release(
                wallet_id=self.wallet_id,
                hold_transaction_id=self.hold_id,
                credit_type_id=self.credit_type_id,
                description=self.description,
                issuer=self.issuer,
                transaction_id=self.transaction_id,
                idempotency_key=f"release_{self.transaction_id}",
                context=release_context
            )
        )
        if success:
            self.hold_id = None
    
    async def __aenter__(self):
        """Enter the context and create a hold if needed."""
        await self.hold()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and handle cleanup.
        
        If an exception occurred or debit wasn't called, release the hold.
        """
        if self.hold_id and not self.debit_amount:
            await self.release()
 