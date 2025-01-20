from typing import Dict, List, Optional

from fastapi import Depends, Query, status

from src.models.base import PaginationRequest
from src.models.products import ProductSubscriptionRequest, ProductSubscriptionResponse
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
from src.utils.router import APIRouter

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
async def create_wallet(wallet_data: CreateWalletRequest) -> WalletResponse:
    """Create a new wallet"""
    return await wallets_service.create_wallet(wallet_request=wallet_data)


@router.get(
    "/{wallet_id}",
    description="Get a wallet by ID",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
)
async def get_wallet(wallet_id: str) -> WalletResponse:
    """Get a wallet by ID"""
    response = await wallets_service.get_wallet_with_balances(wallet_id=wallet_id)
    return response


@router.get(
    "/",
    description="Get wallets",
    response_model=PaginatedWalletResponse,
    status_code=status.HTTP_200_OK,
)
async def get_wallets(
    pagination_request: PaginationRequest = Depends(get_pagination),
    name: Optional[str] = Query(default=None, description="Name of the wallet"),
    context: Dict[str, str] = Depends(dict_parser("context")),
) -> PaginatedWalletResponse:
    """Get all wallets"""
    return await wallets_service.get_wallets(
        pagination_request=pagination_request,
        name=name,
        context=context,
    )


@router.put(
    "/{wallet_id}",
    description="Update an existing wallet",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
)
async def update_wallet(
    wallet_id: str,
    wallet_data: UpdateWalletRequest,
) -> WalletResponse:
    """Update an existing wallet"""
    result = await wallets_service.update_wallet(
        wallet_id=wallet_id, update_wallet_request=wallet_data
    )
    return result


@router.delete(
    "/{wallet_id}",
    description="Delete a wallet",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_wallet(wallet_id: str):
    """Delete a wallet"""
    await wallets_service.delete_wallet(wallet_id=wallet_id)


@router.post(
    "/{wallet_id}/deposit",
    description="Create a deposit transaction for a wallet",
    response_model=TransactionResponse,
)
async def create_deposit_transaction(
    wallet_id: str,
    transaction_request: DepositTransactionRequest,
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
    response_model=List[ProductSubscriptionResponse],
)
async def get_subscriptions(wallet_id: str) -> List[ProductSubscriptionResponse]:
    return await wallets_service.get_subscriptions(wallet_id=wallet_id)
