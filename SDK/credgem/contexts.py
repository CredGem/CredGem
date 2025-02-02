import logging
from typing import Dict, Optional, Any, TYPE_CHECKING

from credgem.api.transactions import TransactionResponse

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
        external_transaction_id: Optional[str] = None,
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
        self.external_transaction_id = external_transaction_id
        self.skip_hold = skip_hold
        self._hold_transaction: Optional[TransactionResponse] = None
        self._debited = False
    
    async def __aenter__(self):
        """Create a hold on the credits if not skipping hold."""
        if not self.skip_hold:
            try:
                self._hold_transaction = await self.client.transactions.hold(
                    wallet_id=self.wallet_id,
                    amount=self.amount,
                    credit_type_id=self.credit_type_id,
                    description=self.description,
                    issuer=self.issuer,
                    context=self.context,
                    external_transaction_id=f"{self.external_transaction_id}_hold" if self.external_transaction_id else None,
                )
            except Exception as e:
                logger.error(f"Failed to create hold: {e}")
                raise
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release the hold if it wasn't debited and not skipping hold."""
        if self._hold_transaction and not self._debited:
            try:
                await self.client.transactions.release(
                    wallet_id=self.wallet_id,
                    hold_transaction_id=self._hold_transaction.id,
                    credit_type_id=self.credit_type_id,
                    description=f"Auto-release of {self.description}",
                    issuer=self.issuer,
                    context=self.context,
                    external_transaction_id=f"{self.external_transaction_id}_release" if self.external_transaction_id else None,
                )
            except Exception as e:
                logger.error(f"API call failed: {e}")
    
    async def debit(self) -> TransactionResponse:
        """Debit the held credits or perform direct debit if skip_hold is True."""
        try:
            if self.skip_hold:
                return await self.client.transactions.debit(
                    wallet_id=self.wallet_id,
                    amount=self.amount,
                    credit_type_id=self.credit_type_id,
                    description=self.description,
                    issuer=self.issuer,
                    context=self.context,
                    external_transaction_id=f"{self.external_transaction_id}_debit" if self.external_transaction_id else None,
                )
            else:
                if not self._hold_transaction:
                    raise ValueError("No active hold to debit")

                response = await self.client.transactions.debit(
                    wallet_id=self.wallet_id,
                    amount=self.amount,
                    credit_type_id=self.credit_type_id,
                    description=self.description,
                    issuer=self.issuer,
                    context=self.context,
                    external_transaction_id=f"{self.external_transaction_id}_debit" if self.external_transaction_id else None,
                    hold_transaction_id=self._hold_transaction.id,
                )
                self._debited = True
                return response
        except Exception as e:
            logger.error(f"Failed to debit: {e}")
            raise
 