from typing import Awaitable, Callable

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from src.core.redis_config import RedisManager
from src.db import transactions as transactions_db
from src.models.transactions import (
    TransactionDBModel,
    TransactionRequestBase,
    TransactionStatus,
)
from src.utils.constants import DUPLICATE_TRANSACTION_ERROR, PG_UNIQUE_VIOLATION_ERROR
from src.utils.ctx_managers import DBSessionCtx, db_session


async def run_managed_transaction(
    wallet_id: str,
    transaction_request: TransactionRequestBase,
    transaction_handler: Callable[
        [TransactionDBModel, DBSessionCtx], Awaitable[TransactionDBModel]
    ],
) -> TransactionDBModel:
    """
    Creates and manages a transaction, handling state updates and error cases.

    Args:
        wallet_id: ID of the wallet to create transaction for
        transaction_request: Request details for the transaction
        transaction_handler: Async function that processes the transaction

    Returns:
        TransactionDBModel: The completed transaction

    Raises:
        HTTPException: If transaction creation fails due to duplicate
        Exception: If transaction processing fails, marks transaction as failed
    """
    try:
        async with db_session() as session_ctx:
            transaction = await transactions_db.create_transaction(
                db=session_ctx.session,
                wallet_id=wallet_id,
                transaction_request=transaction_request,
            )
            session_ctx.add_to_refresh([transaction])

    except IntegrityError as e:
        pgcode = getattr(e.orig, "pgcode", None)
        if pgcode == PG_UNIQUE_VIOLATION_ERROR:
            error_cause = getattr(e.orig, "__cause__", None)
            constraint_name = getattr(error_cause, "constraint_name", "") or ""

            if constraint_name == "ix_transactions_external_id":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=DUPLICATE_TRANSACTION_ERROR,
                )
        raise

    try:
        redis_manager = RedisManager()
        key = redis_manager.create_key(
            namespace="balance_write_lock",
            key=f"{wallet_id}_{transaction_request.credit_type_id}",
        )
        async with redis_manager.client.lock(key, timeout=20):
            async with db_session() as session_ctx:
                return await transaction_handler(transaction, session_ctx)

    except Exception as e:
        async with db_session() as session_ctx:
            await transactions_db.update_transaction(
                session=session_ctx.session,
                transaction_id=transaction.id,
                status=TransactionStatus.FAILED,
            )
        raise e
