from typing import Dict, Optional

from fastapi import APIRouter, Depends, Query

from src.models.base import OrderBy, PaginationRequest
from src.models.transactions import PaginatedTransactionResponse, TransactionResponse
from src.services import transactions_service
from src.utils.dependencies import (
    DateTimeRange,
    dict_parser,
    get_datetime_range,
    get_pagination,
)

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
    credit_type_id: Optional[str] = Query(None),
    wallet_id: Optional[str] = Query(None),
    external_id: Optional[str] = Query(None),
    context: Dict[str, str] = Depends(dict_parser("context")),
    pagination: PaginationRequest = Depends(get_pagination),
    date_range: DateTimeRange = Depends(get_datetime_range),
    order_by: OrderBy = Query(OrderBy.DESC),
) -> PaginatedTransactionResponse:
    return await transactions_service.list_transactions(
        credit_type_id=credit_type_id,
        wallet_id=wallet_id,
        external_id=external_id,
        context=context,
        pagination=pagination,
        date_range=date_range,
        order_by=order_by,
    )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    description="Get details of a specific transaction",
)
async def get_transaction(transaction_id: str) -> TransactionResponse:
    return await transactions_service.get_transaction(transaction_id)
