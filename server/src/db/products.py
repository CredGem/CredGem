from typing import List, Tuple
from uuid import uuid4

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.base import PaginationRequest
from src.models.products import (
    CreateProductRequest,
    CreditSettingsRequest,
    Product,
    ProductSettings,
    ProductStatus,
    UpdateProductRequest,
)


async def create_product(
    db: AsyncSession, product_request: CreateProductRequest
) -> Product:
    product = Product(
        id=str(uuid4()),
        name=product_request.name,
        description=product_request.description,
        status=ProductStatus.ACTIVE,
    )
    db.add(product)
    return product


async def create_product_settings(
    db: AsyncSession, product_id: str, settings_request: List[CreditSettingsRequest]
) -> List[ProductSettings]:
    settings = [
        ProductSettings(
            id=str(uuid4()),
            product_id=product_id,
            credit_type_id=credit_settings.credit_type_id,
            credit_amount=credit_settings.credit_amount,
        )
        for credit_settings in settings_request
    ]

    db.add_all(settings)
    return settings


async def get_product_by_id(db: AsyncSession, product_id: str) -> Product | None:
    query = (
        select(Product)
        .options(joinedload(Product.settings))
        .where(Product.id == product_id)
    )
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()


async def get_products(
    db: AsyncSession, pagination_request: PaginationRequest
) -> Tuple[List[Product], int]:
    # Get total count
    count_query = select(func.count()).select_from(Product)
    total_count = await db.scalar(count_query) or 0

    # Main query with pagination
    query = (
        select(Product)
        .options(joinedload(Product.settings))
        .offset((pagination_request.page - 1) * pagination_request.page_size)
        .limit(pagination_request.page_size)
    )
    result = await db.execute(query)

    return list(result.unique().scalars().all()), total_count


async def update_product(
    db: AsyncSession, product_id: str, request: UpdateProductRequest
) -> Product:
    product = await get_product_by_id(db, product_id)
    if not product:
        raise Exception("Product not found")

    update_values = request.model_dump(exclude_none=True, exclude_unset=True)

    if not update_values:
        return product

    result = await db.execute(
        update(Product)
        .where(Product.id == product_id)
        .values(**update_values)
        .returning(Product)
    )
    updated_product = result.scalar_one()
    return updated_product


async def delete_product(db: AsyncSession, product_id: str) -> None:
    product = await get_product_by_id(db, product_id)
    if not product:
        raise Exception("Product not found")

    await db.execute(delete(Product).where(Product.id == product_id))
