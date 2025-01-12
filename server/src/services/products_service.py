from fastapi import HTTPException

from src.db import products as products_db
from src.models.base import PaginationRequest
from src.models.products import (
    CreateProductRequest,
    PaginatedProductResponse,
    ProductResponse,
    UpdateProductRequest,
)
from src.utils.ctx_managers import db_session


async def create_product_handler(request: CreateProductRequest) -> ProductResponse:
    # first we need to create the product
    async with db_session() as session_ctx:
        product = await products_db.create_product(
            db=session_ctx.session, product_request=request
        )
        settings = await products_db.create_product_settings(
            db=session_ctx.session,
            product_id=product.id,
            settings_request=request.settings,
        )
    return ProductResponse(
        id=product.id,
        created_at=product.created_at,
        updated_at=product.updated_at,
        name=product.name,
        description=product.description,
        status=product.status,
        settings=[setting.to_response() for setting in settings],
    )


async def get_products_handler(
    pagination_request: PaginationRequest,
) -> PaginatedProductResponse:
    async with db_session() as session_ctx:
        products, total_count = await products_db.get_products(
            db=session_ctx.session, pagination_request=pagination_request
        )
        return PaginatedProductResponse(
            page=pagination_request.page,
            page_size=pagination_request.page_size,
            total_count=total_count,
            data=[product.to_response() for product in products],
        )


async def get_product_handler(product_id: str) -> ProductResponse:
    async with db_session() as session_ctx:
        product = await products_db.get_product_by_id(
            session=session_ctx.session, product_id=product_id
        )
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    return product.to_response()


async def update_product_handler(
    product_id: str, request: UpdateProductRequest
) -> ProductResponse:
    async with db_session() as session_ctx:
        product = await products_db.update_product(
            db=session_ctx.session, product_id=product_id, request=request
        )
    return product.to_response()


async def delete_product_handler(product_id: str) -> None:
    async with db_session() as session_ctx:
        await products_db.delete_product(db=session_ctx.session, product_id=product_id)
