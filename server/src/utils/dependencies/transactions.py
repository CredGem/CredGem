from fastapi import Request
from pydantic import BaseModel

from src.models.credit_types import CreditTypeResponse
from src.models.wallets import WalletResponse
from src.services import credit_types_service, wallets_service


class TransactionContext(BaseModel):
    credit_type: CreditTypeResponse
    wallet: WalletResponse


async def transaction_ctx(request: Request) -> TransactionContext:
    """
    Dependency to validate and fetch both wallet and credit type for a transaction.
    Returns a TransactionContext containing the validated wallet and credit type.
    Raises HTTPException if either wallet or credit type is not found.
    """
    wallet_id = request.path_params.get("wallet_id")
    assert wallet_id is not None
    wallet = await wallets_service.get_wallet_by_id(wallet_id=wallet_id)

    body = await request.json()
    credit_type_id = body.get("credit_type_id")
    credit_type = await credit_types_service.get_credit_type(
        credit_type_id=credit_type_id
    )

    return TransactionContext(credit_type=credit_type, wallet=wallet)
