from typing import Dict, Optional

from fastapi import APIRouter, Depends, Query

from src.models.base import PaginationRequest
from src.models.transactions import PaginatedTransactionResponse, TransactionResponse
from src.services import transactions_service
from src.utils.dependencies import (
    DateTimeRange,
    dict_parser,
    get_datetime_range,
    get_pagination,
)
from src.utils.auth import AuthContext, get_auth_context

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.get(
    "/",
    response_model=PaginatedTransactionResponse,
    description="List transactions with optional filters",
)
async def list_transactions(
    wallet_id: Optional[str] = None,
    credit_type_id: Optional[str] = None,
    external_id: Optional[str] = None,
    context: Dict[str, str] = {},
    pagination: PaginationRequest = Depends(),
    date_range: DateTimeRange = Depends(),
    auth: AuthContext = Depends(get_auth_context)
) -> PaginatedTransactionResponse:
    return await transactions_service.list_transactions(
        tenant_id=auth.tenant_id,
        wallet_id=wallet_id,
        credit_type_id=credit_type_id,
        external_id=external_id,
        context=context,
        pagination=pagination,
        date_range=date_range
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    description="Get details of a specific transaction",
)
async def get_transaction(
    transaction_id: str,
    auth: AuthContext = Depends(get_auth_context)
) -> TransactionResponse:
    return await transactions_service.get_transaction(
        transaction_id=transaction_id,
        tenant_id=auth.tenant_id
    )
