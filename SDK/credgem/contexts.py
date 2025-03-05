import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from httpx import HTTPStatusError

from credgem.api.transactions import TransactionResponse
from credgem.models.transactions import DebitRequest, HoldRequest, ReleaseRequest

if TYPE_CHECKING:
    from credgem import CredGemClient

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
        client: "CredGemClient",
        wallet_id: str,
        credit_type_id: str,
        amount: float,
        description: str,
        issuer: str,
        context: Optional[Dict[str, Any]] = None,
        external_id: Optional[str] = None,
        skip_hold: bool = False,
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
        self.context = context
        self.external_id = external_id
        self.skip_hold = skip_hold
        self._hold_transaction: Optional[TransactionResponse] = None
        self._debited = False

    async def _get_existing_transaction(
        self, transaction_type: str
    ) -> Optional[TransactionResponse]:
        """Get an existing transaction by external_id and type."""
        if not self.external_id:
            return None

        external_id = f"{self.external_id}_{transaction_type}"
        transactions = await self.client.transactions.list(
            wallet_id=self.wallet_id, external_id=external_id
        )
        return transactions[0] if transactions else None

    async def __aenter__(self):
        """Create a hold on the credits if not skipping hold."""
        if not self.skip_hold:
            try:
                self._hold_transaction = await self.client.transactions.hold(
                    HoldRequest(
                        wallet_id=self.wallet_id,
                        amount=self.amount,
                        credit_type_id=self.credit_type_id,
                        description=self.description,
                        issuer=self.issuer,
                        context=self.context,
                        external_id=f"{self.external_id}_hold"
                        if self.external_id
                        else None,
                    )
                )
            except HTTPStatusError as e:
                if e.response.status_code == 409:
                    # Look up the existing hold transaction
                    existing_hold = await self._get_existing_transaction("hold")
                    if existing_hold:
                        logger.info(
                            f"Found existing hold for transaction {self.external_id}"
                        )
                        self._hold_transaction = existing_hold
                    else:
                        logger.error(
                            f"409 Conflict but couldn't find existing hold for {self.external_id}"
                        )
                        raise
                else:
                    logger.error(f"Failed to create hold: {e}")
                    raise
            except Exception as e:
                logger.error(f"Failed to create hold: {e}")
                raise
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release the hold if it wasn't debited and not skipping hold."""
        if exc_val is not None and self._hold_transaction:
            try:
                await self.client.transactions.release(
                    ReleaseRequest(
                        wallet_id=self.wallet_id,
                        hold_transaction_id=self._hold_transaction.id,
                        credit_type_id=self.credit_type_id,
                        description=f"Auto-release of {self.description}",
                        issuer=self.issuer,
                        context=self.context,
                        external_id=f"{self.external_id}_release"
                        if self.external_id
                        else None,
                    )
                )
            except HTTPStatusError as e:
                if e.response.status_code == 409:
                    # Check if release already exists
                    existing_release = await self._get_existing_transaction("release")
                    if existing_release:
                        logger.info(
                            f"Release already processed for transaction {self.external_id}"
                        )
                    else:
                        logger.error(
                            f"409 Conflict but couldn't find existing release for {self.external_id}"
                        )
                else:
                    logger.error(f"Failed to release hold: {e}")
            except Exception as e:
                logger.error(f"Failed to release hold: {e}")

    async def debit(
        self,
        amount: Optional[float] = None,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> TransactionResponse:
        """Debit the held credits or perform direct debit if skip_hold is True."""
        try:
            amount = amount or self.amount
            context = {
                **(self.context or {}),
                **(additional_context or {}),
            }
            if self.skip_hold:

                return await self.client.transactions.debit(
                    DebitRequest(
                        wallet_id=self.wallet_id,
                        amount=amount,
                        credit_type_id=self.credit_type_id,
                        description=self.description,
                        issuer=self.issuer,
                        context=context,
                        external_id=f"{self.external_id}_debit"
                        if self.external_id
                        else None,
                    )
                )
            else:
                if not self._hold_transaction:
                    raise ValueError("No active hold to debit")

                try:
                    response = await self.client.transactions.debit(
                        DebitRequest(
                            wallet_id=self.wallet_id,
                            amount=amount,
                            credit_type_id=self.credit_type_id,
                            description=self.description,
                            issuer=self.issuer,
                            context=context,
                            external_id=f"{self.external_id}_debit"
                            if self.external_id
                            else None,
                            hold_transaction_id=self._hold_transaction.id,
                        )
                    )
                    self._debited = True
                    return response
                except HTTPStatusError as e:
                    if e.response.status_code == 409:
                        # Check if debit already exists
                        existing_debit = await self._get_existing_transaction("debit")
                        if existing_debit:
                            logger.info(
                                f"Debit already processed for transaction {self.external_id}"
                            )
                            self._debited = True
                            return existing_debit
                        else:
                            logger.error(
                                f"409 Conflict but couldn't find existing debit for {self.external_id}"
                            )
                            raise
                    raise
        except Exception as e:
            logger.error(f"Failed to debit: {e}")
            raise
