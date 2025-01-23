from typing import Dict, Optional
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import PaginationRequest
from src.models.transactions import (
    HoldStatus,
    PaginatedTransactionDBModel,
    SubscriptionDepositRequest,
    TransactionDBModel,
    TransactionRequestBase,
    TransactionStatus,
    TransactionType,
)
from src.utils.dependencies import DateTimeRange


async def create_transaction(
    db: AsyncSession,
    wallet_id: str,
    transaction_request: TransactionRequestBase,
) -> TransactionDBModel:
    subscription_id = None
    if isinstance(transaction_request, SubscriptionDepositRequest):
        subscription_id = transaction_request.subscription_id

    hold_status = None
    if transaction_request.type == TransactionType.HOLD:
        hold_status = HoldStatus.HELD

    transaction = TransactionDBModel(
        id=str(uuid4()),
        type=transaction_request.type,
        external_transaction_id=transaction_request.external_transaction_id,
        wallet_id=wallet_id,
        credit_type_id=transaction_request.credit_type_id,
        issuer=transaction_request.issuer,
        description=transaction_request.description,
        payload=transaction_request.payload.model_dump(),
        hold_status=hold_status,
        status=TransactionStatus.PENDING,
        subscription_id=subscription_id,
    )
    db.add(transaction)
    return transaction


async def get_transaction(
    session: AsyncSession,
    transaction_id: str,
    transaction_type: Optional[TransactionType] = None,
    credit_type_id: Optional[str] = None,
) -> TransactionDBModel | None:
    query = select(TransactionDBModel).where(
        TransactionDBModel.id == transaction_id,
    )
    if transaction_type:
        query = query.where(TransactionDBModel.type == transaction_type)
    if credit_type_id:
        query = query.where(TransactionDBModel.credit_type_id == credit_type_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def update_transaction(
    session: AsyncSession,
    transaction_id: str,
    status: TransactionStatus | None = None,
    hold_status: HoldStatus | None = None,
    balance_snapshot: dict | None = None,
) -> TransactionDBModel | None:
    update_values = {}
    if status is not None:
        update_values["status"] = status.value
    if hold_status is not None:
        update_values["hold_status"] = hold_status.value
    if balance_snapshot is not None:
        update_values["balance_snapshot"] = balance_snapshot

    result = await session.execute(
        update(TransactionDBModel)
        .where(TransactionDBModel.id == transaction_id)
        .values(**update_values)
        .returning(TransactionDBModel)
    )
    return result.scalar_one_or_none()


async def list_transactions(
    session: AsyncSession,
    wallet_id: Optional[str],
    credit_type_id: Optional[str],
    external_transaction_id: Optional[str],
    pagination: PaginationRequest,
    context: Dict[str, str],
    date_range: DateTimeRange,
) -> PaginatedTransactionDBModel:
    # Base query for both total count and paginated results
    query = select(TransactionDBModel)
    if wallet_id:
        query = query.where(TransactionDBModel.wallet_id == wallet_id)
    if credit_type_id:
        query = query.where(TransactionDBModel.credit_type_id == credit_type_id)
    if external_transaction_id:
        query = query.where(
            TransactionDBModel.external_transaction_id == external_transaction_id
        )
    if context:
        for key, value in context.items():
            query = query.where(TransactionDBModel.context[key].as_string() == value)
    if date_range:
        query = query.where(TransactionDBModel.created_at >= date_range.start_date)
        query = query.where(TransactionDBModel.created_at <= date_range.end_date)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query)

    # Add pagination to the main query
    offset = (pagination.page - 1) * pagination.page_size
    query = query.offset(offset).limit(pagination.page_size)

    # Get paginated results
    result = await session.execute(query)
    transactions = result.scalars().all()

    return PaginatedTransactionDBModel(
        data=list(transactions),
        page=pagination.page,
        page_size=pagination.page_size,
        total_count=total or 0,
    )
