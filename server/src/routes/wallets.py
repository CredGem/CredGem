from typing import Dict, Optional

from fastapi import Depends, Query, status

from src.models.base import PaginationRequest
from src.models.products import (
    PaginatedProductSubscriptionResponse,
    ProductSubscriptionRequest,
    ProductSubscriptionResponse,
)
from src.models.transactions import (
    AdjustTransactionRequest,
    DebitTransactionRequest,
    DepositTransactionRequest,
    HoldTransactionRequest,
    ReleaseTransactionRequest,
    TransactionResponse,
)
from src.models.wallets import (
    CreateWalletRequest,
    PaginatedWalletResponse,
    UpdateWalletRequest,
    WalletResponse,
)
from src.services import wallets_service
from src.utils.dependencies import dict_parser, get_pagination
from src.utils.dependencies.transactions import TransactionContext, transaction_ctx
from src.utils.router import APIRouter
from src.utils.auth import AuthContext, get_auth_context

router = APIRouter(
    prefix="/wallets",
    tags=["wallets"],
)


@router.post(
    "/",
    description="Create a new wallet",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_wallet(
    wallet_request: CreateWalletRequest,
    auth: AuthContext = Depends(get_auth_context)
):
    """Create a new wallet"""
    return await wallets_service.create_wallet(
        wallet_request=wallet_request,
        tenant_id=auth.tenant_id,
        user_id=auth.user_id
    )


@router.get(
    "/{wallet_id}",
    description="Get a wallet by ID",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
)
async def get_wallet(
    wallet_id: str,
    auth: AuthContext = Depends(get_auth_context)
):
    """Get a wallet by ID"""
    return await wallets_service.get_wallet_by_id(
        wallet_id=wallet_id,
        tenant_id=auth.tenant_id
    )


@router.get(
    "/",
    description="Get wallets",
    response_model=PaginatedWalletResponse,
    status_code=status.HTTP_200_OK,
)
async def get_wallets(
    pagination: PaginationRequest = Depends(),
    name: Optional[str] = None,
    context: Optional[Dict[str, str]] = None,
    auth: AuthContext = Depends(get_auth_context)
):
    """Get all wallets"""
    return await wallets_service.get_wallets(
        tenant_id=auth.tenant_id,
        pagination_request=pagination,
        name=name,
        context=context
    )


@router.put(
    "/{wallet_id}",
    description="Update an existing wallet",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
)
async def update_wallet(
    wallet_id: str,
    wallet_request: UpdateWalletRequest,
    auth: AuthContext = Depends(get_auth_context)
):
    """Update an existing wallet"""
    return await wallets_service.update_wallet(
        wallet_id=wallet_id,
        update_wallet_request=wallet_request,
        tenant_id=auth.tenant_id
    )


@router.delete(
    "/{wallet_id}",
    description="Delete a wallet",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_wallet(
    wallet_id: str,
    auth: AuthContext = Depends(get_auth_context)
):
    """Delete a wallet"""
    await wallets_service.delete_wallet(
        wallet_id=wallet_id,
        tenant_id=auth.tenant_id
    )


@router.post(
    "/{wallet_id}/deposit",
    description="Create a deposit transaction for a wallet",
    response_model=TransactionResponse,
)
async def create_deposit_transaction(
    wallet_id: str,
    transaction_request: DepositTransactionRequest,
    transaction_ctx: TransactionContext = Depends(transaction_ctx),
) -> TransactionResponse:
    return await wallets_service.create_deposit_transaction(
        wallet_id=wallet_id, transaction_request=transaction_request
    )


@router.post(
    "/{wallet_id}/debit",
    description="Create a debit transaction for a wallet",
    response_model=TransactionResponse,
)
async def create_debit_transaction(
    wallet_id: str,
    transaction_request: DebitTransactionRequest,
    transaction_ctx: TransactionContext = Depends(transaction_ctx),
) -> TransactionResponse:
    return await wallets_service.create_debit_transaction(
        wallet_id=wallet_id, transaction_request=transaction_request
    )


@router.post(
    "/{wallet_id}/hold",
    description="Create a hold transaction for a wallet",
    response_model=TransactionResponse,
)
async def create_hold_transaction(
    wallet_id: str,
    transaction_request: HoldTransactionRequest,
    transaction_ctx: TransactionContext = Depends(transaction_ctx),
) -> TransactionResponse:
    return await wallets_service.create_hold_transaction(
        wallet_id=wallet_id, transaction_request=transaction_request
    )


@router.post(
    "/{wallet_id}/release",
    description="Create a release transaction for a wallet",
    response_model=TransactionResponse,
)
async def create_release_transaction(
    wallet_id: str,
    transaction_request: ReleaseTransactionRequest,
    transaction_ctx: TransactionContext = Depends(transaction_ctx),
) -> TransactionResponse:
    return await wallets_service.create_release_transaction(
        wallet_id=wallet_id, transaction_request=transaction_request
    )


@router.post(
    "/{wallet_id}/adjust",
    description="Create an adjust transaction for a wallet",
    response_model=TransactionResponse,
)
async def create_adjust_transaction(
    wallet_id: str,
    transaction_request: AdjustTransactionRequest,
    transaction_ctx: TransactionContext = Depends(transaction_ctx),
) -> TransactionResponse:
    return await wallets_service.create_adjust_transaction(
        wallet_id=wallet_id, transaction_request=transaction_request
    )


@router.post(
    "/{wallet_id}/subscriptions",
    description="Subscribe to a product",
    response_model=ProductSubscriptionResponse,
)
async def subscribe_to_product(
    wallet_id: str,
    subscription_request: ProductSubscriptionRequest,
) -> ProductSubscriptionResponse:
    return await wallets_service.subscribe_to_product(
        wallet_id=wallet_id,
        subscription_request=subscription_request,
    )


@router.get(
    "/{wallet_id}/subscriptions",
    description="Get subscriptions for a wallet",
    response_model=PaginatedProductSubscriptionResponse,
)
async def get_subscriptions(
    wallet_id: str,
    pagination_request: PaginationRequest = Depends(get_pagination),
) -> PaginatedProductSubscriptionResponse:
    return await wallets_service.get_subscriptions(
        wallet_id=wallet_id, pagination_request=pagination_request
    )
