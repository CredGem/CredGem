from typing import Optional
from uuid import uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.base import PaginationRequest
from src.models.wallets import CreateWalletRequest, UpdateWalletRequest, Wallet


async def get_wallet(
    session: AsyncSession, 
    wallet_id: str,
    tenant_id: str
) -> Wallet | None:
    """Get a wallet by ID"""
    return await session.get(
        Wallet, 
        wallet_id,
        options=[selectinload(Wallet._balances)],
        execution_options={"populate_existing": True},
        with_for_update={"key_share": True},
        filter_by={"tenant_id": tenant_id}
    )


async def get_wallet_with_balances(
    session: AsyncSession, 
    wallet_id: str,
    tenant_id: str
) -> Wallet | None:
    """Get a wallet by ID and join its balances"""
    query = (
        select(Wallet)
        .options(selectinload(Wallet._balances))
        .where(
            Wallet.id == wallet_id,
            Wallet.tenant_id == tenant_id
        )
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_wallets(
    session: AsyncSession,
    tenant_id: str,
    pagination_request: PaginationRequest,
    name: Optional[str] = None,
    context: Optional[dict] = None,
) -> tuple[list[Wallet], int]:
    """Get all wallets with pagination

    Returns:
        tuple: (list of wallets, total count)
    """

    def apply_filters(query):
        query = query.where(Wallet.tenant_id == tenant_id)
        if name:
            query = query.where(Wallet.name.ilike(f"%{name}%"))
        if context:
            for key, value in context.items():
                query = query.where(Wallet.context[key].as_string() == str(value))
        return query

    # Build base query
    query = select(Wallet)
    query = apply_filters(query)

    # Get total count
    count_query = select(func.count()).select_from(Wallet)
    count_query = apply_filters(count_query)
    total_count = await session.scalar(count_query)

    if total_count == 0:
        return [], 0

    # Apply pagination
    query = (
        query.order_by(Wallet.created_at.desc())
        .offset((pagination_request.page - 1) * pagination_request.page_size)
        .limit(pagination_request.page_size)
    )

    result = await session.execute(query)
    return list(result.scalars().all()), total_count or 0


async def create_wallet(
    session: AsyncSession, 
    wallet_request: CreateWalletRequest,
    tenant_id: str,
    user_id: str
) -> Wallet:
    """Create a new wallet"""
    wallet = Wallet(
        id=str(uuid4()),
        name=wallet_request.name,
        context=wallet_request.context,
        external_id=wallet_request.external_id,
        tenant_id=tenant_id,
        user_id=user_id
    )
    session.add(wallet)
    return wallet


async def update_wallet(
    session: AsyncSession, 
    wallet_id: str, 
    update_wallet_request: UpdateWalletRequest,
    tenant_id: str
) -> Optional[Wallet]:
    """Update an existing wallet

    Args:
        db: Database session
        wallet_id: ID of the wallet to update
        update_wallet_request: Request containing fields to update
        tenant_id: ID of the tenant

    Returns:
        Updated wallet if found, None otherwise
    """
    wallet = await get_wallet(session, wallet_id, tenant_id)
    if not wallet:
        return None

    # Update fields if provided in request
    if update_wallet_request.name is not None:
        wallet.name = update_wallet_request.name
    if update_wallet_request.context is not None:
        wallet.context = update_wallet_request.context

    return wallet


async def delete_wallet(
    session: AsyncSession, 
    wallet_id: str,
    tenant_id: str
) -> bool:
    """Delete a wallet"""
    result = await session.execute(
        delete(Wallet).where(
            Wallet.id == wallet_id,
            Wallet.tenant_id == tenant_id
        )
    )
    return result.rowcount > 0
