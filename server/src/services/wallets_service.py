import asyncio
from logging import getLogger
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import balances as balances_db
from src.db import products as products_db
from src.db import transactions as transactions_db
from src.db import wallets
from src.models.base import PaginationRequest
from src.models.products import (
    PaginatedProductSubscriptionResponse,
    ProductSettings,
    ProductSubscription,
    ProductSubscriptionRequest,
    ProductSubscriptionResponse,
    PydanticProductSettings,
    SubscriptionMode,
    SubscriptionResult,
    SubscriptionStatus,
    SubscriptionType,
)
from src.models.transactions import (
    AdjustTransactionRequest,
    BalanceSnapshot,
    DebitTransactionRequest,
    DepositTransactionRequest,
    DepositTransactionRequestPayload,
    HoldStatus,
    HoldTransactionRequest,
    HoldTransactionRequestPayload,
    ReleaseTransactionRequest,
    SubscriptionDepositPayload,
    TransactionDBModel,
    TransactionResponse,
    TransactionStatus,
    TransactionType,
)
from src.models.wallets import (
    CreateWalletRequest,
    PaginatedWalletResponse,
    UpdateWalletRequest,
    WalletResponse,
)
from src.utils.constants import (
    BALANCE_NOT_FOUND_ERROR,
    HOLD_AMOUNT_EXCEEDS_ERROR,
    HOLD_TRANSACTION_NOT_FOUND_ERROR,
    HOLD_TRANSACTION_NOT_HELD_ERROR,
    INSUFFICIENT_BALANCE_ERROR,
    WALLET_NOT_FOUND_ERROR,
)
from src.utils.ctx_managers import DBSessionCtx, db_session
from src.utils.transactions import run_managed_transaction

logger = getLogger(__name__)


async def get_wallet_by_id(wallet_id: str) -> WalletResponse:
    """Get a wallet by ID"""
    async with db_session(read_only=True) as session_ctx:
        wallet = await wallets.get_wallet(
            session=session_ctx.session, wallet_id=wallet_id
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=WALLET_NOT_FOUND_ERROR
            )
        session_ctx.add_to_refresh([wallet])
    return wallet.to_response()


async def get_wallet_with_balances(wallet_id: str) -> WalletResponse:
    """Get a wallet by ID and join its balances"""
    async with db_session(read_only=True) as session_ctx:
        wallet = await wallets.get_wallet_with_balances(
            session=session_ctx.session, wallet_id=wallet_id
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=WALLET_NOT_FOUND_ERROR
            )
        session_ctx.add_to_refresh([wallet])
    return wallet.to_response()


async def get_wallets(
    pagination_request: PaginationRequest,
    name: Optional[str] = None,
    context: Optional[dict] = None,
) -> PaginatedWalletResponse:
    """Get all wallets"""
    async with db_session(read_only=True) as session_ctx:
        wallet_list, total_count = await wallets.get_wallets(
            session=session_ctx.session,
            pagination_request=pagination_request,
            name=name,
            context=context,
        )
    return PaginatedWalletResponse(
        page=pagination_request.page,
        page_size=pagination_request.page_size,
        total_count=total_count,
        data=[wallet.to_response() for wallet in wallet_list],
    )


async def create_wallet(wallet_request: CreateWalletRequest) -> WalletResponse:
    """Create a new wallet"""
    async with db_session() as session_ctx:
        wallet = await wallets.create_wallet(
            session=session_ctx.session, wallet_request=wallet_request
        )
        session_ctx.add_to_refresh([wallet])
    return wallet.to_response()


async def update_wallet(
    wallet_id: str, update_wallet_request: UpdateWalletRequest
) -> WalletResponse:
    """Update an existing wallet"""
    async with db_session() as session_ctx:
        wallet = await wallets.update_wallet(
            session=session_ctx.session,
            wallet_id=wallet_id,
            update_wallet_request=update_wallet_request,
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=WALLET_NOT_FOUND_ERROR
            )
        session_ctx.add_to_refresh([wallet])
    return wallet.to_response()


async def delete_wallet(wallet_id: str) -> None:
    """Delete a wallet"""
    async with db_session() as session_ctx:
        wallet = await wallets.delete_wallet(
            session=session_ctx.session,
            wallet_id=wallet_id,
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=WALLET_NOT_FOUND_ERROR
            )


async def _deposit_transaction_handler(
    pending_transaction: TransactionDBModel,
    session_ctx: DBSessionCtx,
) -> TransactionDBModel:
    session = session_ctx.session
    updated_balance = await balances_db.deposit_balance(
        session=session,
        wallet_id=pending_transaction.wallet_id,
        credit_type_id=pending_transaction.credit_type_id,
        amount=pending_transaction.payload["amount"],
    )
    balance_snapshot = BalanceSnapshot(
        available=updated_balance.available,
        held=updated_balance.held,
        spent=updated_balance.spent,
        overall_spent=updated_balance.overall_spent,
    )
    updated_transaction = await transactions_db.update_transaction(
        session=session,
        transaction_id=pending_transaction.id,
        balance_snapshot=balance_snapshot.model_dump(),
        status=TransactionStatus.COMPLETED,
    )
    return updated_transaction


async def create_deposit_transaction(
    wallet_id: str, transaction_request: DepositTransactionRequest
) -> TransactionResponse:
    transaction_result = await run_managed_transaction(
        wallet_id=wallet_id,
        transaction_request=transaction_request,
        transaction_handler=_deposit_transaction_handler,
    )
    return transaction_result.to_response()


async def _debit_transaction_handler(
    pending_transaction: TransactionDBModel,
    session_ctx: DBSessionCtx,
) -> TransactionDBModel:
    session = session_ctx.session
    hold_transaction_id = pending_transaction.payload["hold_transaction_id"]
    hold_transaction_payload = None
    held_amount = 0
    remaining_held_amount = 0

    if hold_transaction_id:
        hold_transaction_payload = await _get_and_validate_hold(
            transaction_request=pending_transaction, session=session
        )
        held_amount = hold_transaction_payload.amount
        remaining_held_amount = held_amount - pending_transaction.payload["amount"]

    # Calculate debit amount based on hold status
    debit_amount = (
        -remaining_held_amount
        if hold_transaction_payload
        else pending_transaction.payload["amount"]
    )
    spent = pending_transaction.payload["amount"]

    updated_balance = await balances_db.debit_balance(
        session=session,
        wallet_id=pending_transaction.wallet_id,
        credit_type_id=pending_transaction.credit_type_id,
        amount=debit_amount,
        held_amount=held_amount,
        spent=spent,
    )
    if not updated_balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=BALANCE_NOT_FOUND_ERROR
        )
    if updated_balance.available < 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=INSUFFICIENT_BALANCE_ERROR,
        )

    balance_snapshot = BalanceSnapshot(
        available=updated_balance.available,
        held=updated_balance.held,
        spent=updated_balance.spent,
        overall_spent=updated_balance.overall_spent,
    )

    if hold_transaction_payload:
        await transactions_db.update_transaction(
            session=session,
            transaction_id=hold_transaction_id,
            hold_status=HoldStatus.USED,
        )

    updated_transaction = await transactions_db.update_transaction(
        session=session,
        transaction_id=pending_transaction.id,
        balance_snapshot=balance_snapshot.model_dump(),
        status=TransactionStatus.COMPLETED,
    )
    return updated_transaction


async def _get_and_validate_hold(
    transaction_request: TransactionDBModel, session: AsyncSession
) -> HoldTransactionRequestPayload:
    assert transaction_request.payload["hold_transaction_id"]

    hold_transaction = await transactions_db.get_transaction(
        transaction_id=transaction_request.payload["hold_transaction_id"],
        transaction_type=TransactionType.HOLD,
        credit_type_id=transaction_request.credit_type_id,
        session=session,
    )
    if not hold_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=HOLD_TRANSACTION_NOT_FOUND_ERROR,
        )

    if hold_transaction.hold_status != HoldStatus.HELD.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=HOLD_TRANSACTION_NOT_HELD_ERROR,
        )

    hold_transaction_payload = HoldTransactionRequestPayload(**hold_transaction.payload)

    if hold_transaction_payload.amount < transaction_request.payload["amount"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=HOLD_AMOUNT_EXCEEDS_ERROR,
        )
    return hold_transaction_payload


async def create_debit_transaction(
    wallet_id: str, transaction_request: DebitTransactionRequest
) -> TransactionResponse:
    transaction_result = await run_managed_transaction(
        wallet_id=wallet_id,
        transaction_request=transaction_request,
        transaction_handler=_debit_transaction_handler,
    )
    return transaction_result.to_response()


async def _hold_transaction_handler(
    pending_transaction: TransactionDBModel,
    session_ctx: DBSessionCtx,
) -> TransactionDBModel:
    session = session_ctx.session
    updated_balance = await balances_db.hold_balance(
        session=session,
        wallet_id=pending_transaction.wallet_id,
        credit_type_id=pending_transaction.credit_type_id,
        amount=pending_transaction.payload["amount"],
    )
    if not updated_balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=BALANCE_NOT_FOUND_ERROR
        )
    if updated_balance.held < 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=INSUFFICIENT_BALANCE_ERROR,
        )

    balance_snapshot = BalanceSnapshot(
        available=updated_balance.available,
        held=updated_balance.held,
        spent=updated_balance.spent,
        overall_spent=updated_balance.overall_spent,
    )

    updated_transaction = await transactions_db.update_transaction(
        session=session,
        transaction_id=pending_transaction.id,
        status=TransactionStatus.COMPLETED,
        balance_snapshot=balance_snapshot.model_dump(),
        hold_status=HoldStatus.HELD,
    )
    assert updated_transaction is not None
    return updated_transaction


async def create_hold_transaction(
    wallet_id: str, transaction_request: HoldTransactionRequest
) -> TransactionResponse:
    transaction_result = await run_managed_transaction(
        wallet_id=wallet_id,
        transaction_request=transaction_request,
        transaction_handler=_hold_transaction_handler,
    )
    return transaction_result.to_response()


async def _release_transaction_handler(
    pending_transaction: TransactionDBModel,
    session_ctx: DBSessionCtx,
) -> TransactionDBModel:
    session = session_ctx.session
    hold_transaction = await transactions_db.get_transaction(
        transaction_id=pending_transaction.payload["hold_transaction_id"],
        credit_type_id=pending_transaction.credit_type_id,
        transaction_type=TransactionType.HOLD,
        session=session,
    )
    if not hold_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=HOLD_TRANSACTION_NOT_FOUND_ERROR,
        )

    if hold_transaction.hold_status != HoldStatus.HELD.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=HOLD_TRANSACTION_NOT_HELD_ERROR,
        )

    hold_transaction_payload = HoldTransactionRequestPayload(**hold_transaction.payload)
    updated_balance = await balances_db.release_balance(
        session=session,
        wallet_id=pending_transaction.wallet_id,
        credit_type_id=pending_transaction.credit_type_id,
        amount=hold_transaction_payload.amount,
    )
    if not updated_balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=BALANCE_NOT_FOUND_ERROR
        )
    if updated_balance.held < 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=INSUFFICIENT_BALANCE_ERROR,
        )

    balance_snapshot = BalanceSnapshot(
        available=updated_balance.available,
        held=updated_balance.held,
        spent=updated_balance.spent,
        overall_spent=updated_balance.overall_spent,
    )

    update_hold_status = transactions_db.update_transaction(
        session=session,
        transaction_id=hold_transaction.id,
        hold_status=HoldStatus.RELEASED,
        balance_snapshot=balance_snapshot.model_dump(),
    )
    update_hold_transaction = transactions_db.update_transaction(
        session=session,
        transaction_id=pending_transaction.id,
        status=TransactionStatus.COMPLETED,
    )

    [_, updated_transaction] = await asyncio.gather(
        update_hold_status,
        update_hold_transaction,
    )
    assert updated_transaction is not None
    return updated_transaction


async def create_release_transaction(
    wallet_id: str, transaction_request: ReleaseTransactionRequest
) -> TransactionResponse:
    transaction_result = await run_managed_transaction(
        wallet_id=wallet_id,
        transaction_request=transaction_request,
        transaction_handler=_release_transaction_handler,
    )
    return transaction_result.to_response()


async def _adjust_transaction_handler(
    pending_transaction: TransactionDBModel,
    session_ctx: DBSessionCtx,
) -> TransactionDBModel:
    session = session_ctx.session
    updated_balance = await balances_db.adjust_balance(
        session=session,
        wallet_id=pending_transaction.wallet_id,
        credit_type_id=pending_transaction.credit_type_id,
        amount=pending_transaction.payload["amount"],
        reset_spent=pending_transaction.payload.get("reset_spent", False),
    )
    if not updated_balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=BALANCE_NOT_FOUND_ERROR
        )
    if updated_balance.available < 0 or updated_balance.held < 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=INSUFFICIENT_BALANCE_ERROR,
        )

    balance_snapshot = BalanceSnapshot(
        available=updated_balance.available,
        held=updated_balance.held,
        spent=updated_balance.spent,
        overall_spent=updated_balance.overall_spent,
    )

    updated_transaction = await transactions_db.update_transaction(
        session=session,
        transaction_id=pending_transaction.id,
        status=TransactionStatus.COMPLETED,
        balance_snapshot=balance_snapshot.model_dump(),
    )
    assert updated_transaction is not None
    return updated_transaction


async def create_adjust_transaction(
    wallet_id: str, transaction_request: AdjustTransactionRequest
) -> TransactionResponse:
    transaction_result = await run_managed_transaction(
        wallet_id=wallet_id,
        transaction_request=transaction_request,
        transaction_handler=_adjust_transaction_handler,
    )
    return transaction_result.to_response()


async def get_subscriptions(
    wallet_id: str,
    pagination_request: PaginationRequest,
) -> PaginatedProductSubscriptionResponse:
    async with db_session(read_only=True) as session_ctx:
        subscriptions, total_count = await products_db.get_subscriptions(
            session=session_ctx.session,
            wallet_id=wallet_id,
            pagination_request=pagination_request,
        )
    return PaginatedProductSubscriptionResponse(
        page=pagination_request.page,
        page_size=pagination_request.page_size,
        total_count=total_count,
        data=[
            subscription.to_response(include_product=True)
            for subscription in subscriptions
        ],
    )


async def subscribe_to_product(
    wallet_id: str,
    subscription_request: ProductSubscriptionRequest,
) -> ProductSubscriptionResponse:
    if subscription_request.type != SubscriptionType.ONE_TIME:
        raise HTTPException(
            status_code=400,
            detail="Only one-time subscriptions are currently supported",
        )

    if subscription_request.mode != SubscriptionMode.ADD:
        raise HTTPException(
            status_code=400, detail="Only add mode is currently supported"
        )

    async with db_session() as session_ctx:
        product = await products_db.get_product_by_id(
            session=session_ctx.session,
            product_id=subscription_request.product_id,
        )
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        settings_snapshot = [
            PydanticProductSettings(
                id=setting.id,
                product_id=setting.product_id,
                credit_type_id=setting.credit_type_id,
                credit_amount=setting.credit_amount,
            )
            for setting in product.settings
        ]

        subscription = await products_db.create_product_subscription(
            session=session_ctx.session,
            wallet_id=wallet_id,
            subscription_request=subscription_request,
            settings_snapshot=settings_snapshot,
        )
        session_ctx.add_to_refresh([subscription])

    results = await _handle_one_time_add_subscription(
        subscription=subscription,
        settings=product.settings,
    )

    async with db_session() as session_ctx:
        has_failures = any(not result.success for result in results)
        final_status = (
            SubscriptionStatus.FAILED if has_failures else SubscriptionStatus.COMPLETED
        )
        subscription = await products_db.update_product_subscription_status(
            session=session_ctx.session,
            subscription_id=subscription.id,
            status=final_status,
        )
        session_ctx.add_to_refresh([subscription])

    return subscription.to_response()


async def _handle_one_time_add_subscription(
    subscription: ProductSubscription,
    settings: List[ProductSettings],
) -> List[SubscriptionResult]:
    results: List[SubscriptionResult] = []

    for setting in settings:
        deposit_request = SubscriptionDepositPayload(
            subscription_id=subscription.id,
            credit_type_id=setting.credit_type_id,
            description="Subscription deposit",
            payload=DepositTransactionRequestPayload(
                amount=setting.credit_amount,
            ),
            issuer="subscription",
        )
        try:
            deposit_result = await create_deposit_transaction(
                wallet_id=subscription.wallet_id, transaction_request=deposit_request
            )
            results.append(
                SubscriptionResult(
                    setting_id=setting.id, success=True, message=deposit_result.id
                )
            )
        except Exception as e:
            logger.info(f"Failed to deposit for setting {setting.id}: {e}")
            results.append(
                SubscriptionResult(setting_id=setting.id, success=False, message=str(e))
            )

    return results
