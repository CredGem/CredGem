from asyncio import gather
from typing import List, Tuple
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.base import PaginationRequest
from src.models.products import (
    CreateProductRequest,
    CreditSettingsRequest,
    Product,
    ProductSettings,
    ProductStatus,
    ProductSubscription,
    ProductSubscriptionRequest,
    PydanticProductSettings,
    SubscriptionStatus,
    UpdateProductRequest,
)


async def create_product(
    db: AsyncSession, 
    product_request: CreateProductRequest,
    tenant_id: str,
    user_id: str
) -> Product:
    product = Product(
        id=str(uuid4()),
        name=product_request.name,
        description=product_request.description,
        status=ProductStatus.ACTIVE,
        tenant_id=tenant_id,
        user_id=user_id
    )
    db.add(product)
    return product


async def create_product_settings(
    db: AsyncSession, 
    product_id: str, 
    settings_request: List[CreditSettingsRequest],
    tenant_id: str,
    user_id: str
) -> List[ProductSettings]:
    settings = [
        ProductSettings(
            id=str(uuid4()),
            product_id=product_id,
            credit_type_id=credit_settings.credit_type_id,
            credit_amount=credit_settings.credit_amount,
            tenant_id=tenant_id,
            user_id=user_id
        )
        for credit_settings in settings_request
    ]

    db.add_all(settings)
    return settings


async def get_product_by_id(
    session: AsyncSession, 
    product_id: str,
    tenant_id: str
) -> Product | None:
    query = (
        select(Product)
        .options(joinedload(Product.settings))
        .where(
            Product.id == product_id,
            Product.tenant_id == tenant_id
        )
    )
    result = await session.execute(query)
    return result.unique().scalar_one_or_none()


async def get_products(
    db: AsyncSession, 
    pagination_request: PaginationRequest,
    tenant_id: str
) -> Tuple[List[Product], int]:
    # Get total count
    count_query = select(func.count()).select_from(
        select(Product).where(Product.tenant_id == tenant_id).subquery()
    )
    total_count = await db.scalar(count_query) or 0

    # Main query with pagination
    query = (
        select(Product)
        .options(joinedload(Product.settings))
        .where(Product.tenant_id == tenant_id)
        .offset((pagination_request.page - 1) * pagination_request.page_size)
        .limit(pagination_request.page_size)
    )
    result = await db.execute(query)

    return list(result.unique().scalars().all()), total_count


async def update_product(
    db: AsyncSession, 
    product_id: str, 
    request: UpdateProductRequest,
    tenant_id: str
) -> Product:
    product = await get_product_by_id(db, product_id, tenant_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_values = request.model_dump(exclude_none=True, exclude_unset=True)

    if not update_values:
        return product

    result = await db.execute(
        update(Product)
        .where(
            Product.id == product_id,
            Product.tenant_id == tenant_id
        )
        .values(**update_values)
        .returning(Product)
    )
    updated_product = result.scalar_one()
    return updated_product


async def get_subscriptions(
    session: AsyncSession, 
    wallet_id: str, 
    pagination_request: PaginationRequest,
    tenant_id: str
) -> Tuple[List[ProductSubscription], int]:
    # Prepare both queries
    count_query = (
        select(func.count(ProductSubscription.id))
        .select_from(ProductSubscription)
        .where(
            ProductSubscription.wallet_id == wallet_id,
            ProductSubscription.tenant_id == tenant_id
        )
    )

    main_query = (
        select(ProductSubscription)
        .join(Product, ProductSubscription.product_id == Product.id)
        .options(joinedload(ProductSubscription.product).joinedload(Product.settings))
        .where(
            ProductSubscription.wallet_id == wallet_id,
            ProductSubscription.tenant_id == tenant_id
        )
        .order_by(ProductSubscription.id)
        .offset((pagination_request.page - 1) * pagination_request.page_size)
        .limit(pagination_request.page_size)
    )

    # Execute both queries in parallel
    count_result, subscriptions_result = await gather(
        session.scalar(count_query), session.execute(main_query)
    )

    total_count = count_result or 0
    subscriptions = list(subscriptions_result.unique().scalars().all())

    return subscriptions, total_count


async def create_product_subscription(
    session: AsyncSession,
    wallet_id: str,
    subscription_request: ProductSubscriptionRequest,
    settings_snapshot: List[PydanticProductSettings],
    tenant_id: str,
    user_id: str
) -> ProductSubscription:
    subscription = ProductSubscription(
        id=str(uuid4()),
        wallet_id=wallet_id,
        product_id=subscription_request.product_id,
        status=SubscriptionStatus.PENDING,
        type=subscription_request.type,
        mode=subscription_request.mode,
        settings_snapshot=[setting.model_dump() for setting in settings_snapshot],
        tenant_id=tenant_id,
        user_id=user_id
    )
    session.add(subscription)
    return subscription


async def update_product_subscription_status(
    session: AsyncSession, 
    subscription_id: str, 
    status: SubscriptionStatus,
    tenant_id: str
) -> ProductSubscription:
    result = await session.execute(
        update(ProductSubscription)
        .where(
            ProductSubscription.id == subscription_id,
            ProductSubscription.tenant_id == tenant_id
        )
        .values(status=status)
        .returning(ProductSubscription)
    )
    return result.scalar_one()
