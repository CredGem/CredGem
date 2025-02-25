from typing import Dict, Optional

from fastapi import HTTPException

from src.db import transactions as transactions_db
from src.models.base import PaginationRequest
from src.models.transactions import PaginatedTransactionResponse, TransactionResponse
from src.utils.ctx_managers import db_session
from src.utils.dependencies import DateTimeRange


async def get_transaction(transaction_id: str) -> TransactionResponse:
    async with db_session() as session_ctx:
        session = session_ctx.session
        transaction = await transactions_db.get_transaction(
            session=session, transaction_id=transaction_id
        )
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction.to_response()


async def get_transaction_by_external_id(
    external_transaction_id: str,
) -> TransactionResponse | None:
    async with db_session() as session_ctx:
        session = session_ctx.session
        transaction = await transactions_db.get_transaction_by_external_id(
            session=session, external_transaction_id=external_transaction_id
        )
    return transaction.to_response() if transaction else None


async def list_transactions(
    wallet_id: Optional[str],
    credit_type_id: Optional[str],
    external_transaction_id: Optional[str],
    context: Dict[str, str],
    pagination: PaginationRequest,
    date_range: DateTimeRange,
) -> PaginatedTransactionResponse:
    async with db_session() as session_ctx:
        session = session_ctx.session
        transactions = await transactions_db.list_transactions(
            session=session,
            wallet_id=wallet_id,
            credit_type_id=credit_type_id,
            external_transaction_id=external_transaction_id,
            pagination=pagination,
            context=context,
            date_range=date_range,
        )
    data = [transaction.to_response() for transaction in transactions.data]
    return PaginatedTransactionResponse(
        data=data,
        page=transactions.page,
        page_size=transactions.page_size,
        total_count=transactions.total_count,
    )
