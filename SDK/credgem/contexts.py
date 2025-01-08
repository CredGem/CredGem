import uuid
import logging
from typing import Optional, Dict, Any, Tuple
from decimal import Decimal

from httpx import HTTPStatusError

from credgem.api.base import BaseAPI
from credgem.exceptions import InsufficientCreditsError

logger = logging.getLogger(__name__)


class DrawCredits:
    """Context manager for handling credit operations with hold-debit-release flow"""

    def __init__(
        self,
        client: BaseAPI,
        wallet_id: str,
        credit_type_id: str,
        description: str,
        issuer: str,
        amount: Optional[Decimal] = None,
        transaction_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        skip_hold: bool = False,
    ):
        """
        Initialize a new DrawCredits context.

        Args:
            client: The CredGem client instance
            wallet_id: The wallet to draw credits from
            credit_type_id: The type of credits to use
            description: Description of the transaction
            issuer: The system/service performing the operation
            amount: Amount to hold (required if skip_hold is False)
            transaction_id: Optional custom transaction ID (UUID will be generated if not provided)
            context: Optional additional context for the transaction
            skip_hold: If True, skips the automatic hold on enter
        """
        self.client = client
        self.wallet_id = wallet_id
        self.credit_type_id = credit_type_id
        self.amount = amount
        self.description = description
        self.issuer = issuer
        self.transaction_id = transaction_id or str(uuid.uuid4())
        self.context = context or {}
        self.skip_hold = skip_hold
        
        # State tracking
        self.hold_id = None
        self._hold_response = None
        self._debit_called = False

        if not skip_hold and amount is None:
            raise ValueError("Amount must be provided when skip_hold is False")

    async def _handle_api_call(self, api_call) -> Tuple[bool, Any]:
        """
        Handle API calls with proper error handling.
        Returns (success: bool, response: Any)
        409 status code is considered a success as it means the operation was already completed.
        """
        try:
            response = await api_call
            return True, response
        except HTTPStatusError as e:
            if e.response.status_code == 409:
                logger.info("Operation already completed (409 Conflict), treating as success")
                return True, None
            if e.response.status_code == 402:
                raise InsufficientCreditsError(
                    f"Insufficient credits of type {self.credit_type_id}"
                ) from e
            raise
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise

    async def debit(
        self,
        amount: Optional[Decimal] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Debit credits from the wallet.
        If a hold exists, it will be used, otherwise performs a direct debit.
        
        Args:
            amount: Optional amount to debit. If not provided and a hold exists, uses the held amount
            context: Optional context to override or merge with the initial context
        """
        # Merge contexts if provided, otherwise use original
        debit_context = {**self.context, **(context or {})}

        logger.info(
            f"Debiting credits for wallet {self.wallet_id}"
            + (f" with amount {amount}" if amount else "")
        )
        success, _ = await self._handle_api_call(
            self.client.transactions.debit(
                wallet_id=self.wallet_id,
                amount=amount,  # Server will use hold amount if None and hold_id is provided
                credit_type_id=self.credit_type_id,
                description=self.description,
                issuer=self.issuer,
                hold_transaction_id=self.hold_id,  # None if no hold exists
                idempotency_key=f"debit_{self.transaction_id}",
                context=debit_context
            )
        )
        if success:
            self._debit_called = True

    async def release(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Release the current hold.
        
        Args:
            context: Optional context to override or merge with the initial context
        """
        if not self.hold_id:
            raise ValueError("No active hold to release")

        # Merge contexts if provided, otherwise use original
        release_context = {**self.context, **(context or {})}

        logger.info(
            f"Releasing hold {self.hold_id} for wallet {self.wallet_id}"
        )
        await self._handle_api_call(
            self.client.transactions.release(
                wallet_id=self.wallet_id,
                hold_transaction_id=self.hold_id,
                credit_type_id=self.credit_type_id,
                description=f"Release hold",
                issuer=self.issuer,
                idempotency_key=f"release_{self.transaction_id}",
                context=release_context
            )
        )

    async def __aenter__(self):
        if not self.skip_hold:
            logger.info(
                f"Creating hold for {self.amount} credits for wallet {self.wallet_id}"
            )
            success, response = await self._handle_api_call(
                self.client.transactions.hold(
                    wallet_id=self.wallet_id,
                    amount=self.amount,
                    credit_type_id=self.credit_type_id,
                    description=self.description,
                    issuer=self.issuer,
                    idempotency_key=f"hold_{self.transaction_id}",
                    context=self.context
                )
            )
            if success and response:
                self._hold_response = response
                self.hold_id = response.id
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self.hold_id:
            return

        # If there was an error or debit wasn't called, release the hold
        if exc_type or not self._debit_called:
            try:
                logger.info(
                    f"Releasing hold {self.hold_id} for wallet {self.wallet_id} "
                    f"due to {'error' if exc_type else 'no debit called'}"
                )
                await self.release(
                    context={
                        "status": "error" if exc_type else "not_debited",
                        "error": str(exc_val) if exc_type else None
                    }
                )
            except Exception as e:
                logger.error(f"Error releasing hold: {e}")
                raise
 