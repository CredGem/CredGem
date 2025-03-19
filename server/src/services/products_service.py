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


async def create_product_handler(
    request: CreateProductRequest,
    tenant_id: str,
    user_id: str
) -> ProductResponse:
    # first we need to create the product
    async with db_session() as session_ctx:
        product = await products_db.create_product(
            db=session_ctx.session, 
            product_request=request,
            tenant_id=tenant_id,
            user_id=user_id
        )
        settings = await products_db.create_product_settings(
            db=session_ctx.session,
            product_id=product.id,
            settings_request=request.settings,
            tenant_id=tenant_id,
            user_id=user_id
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
    tenant_id: str
) -> PaginatedProductResponse:
    async with db_session() as session_ctx:
        products, total_count = await products_db.get_products(
            db=session_ctx.session, 
            pagination_request=pagination_request,
            tenant_id=tenant_id
        )
        return PaginatedProductResponse(
            page=pagination_request.page,
            page_size=pagination_request.page_size,
            total_count=total_count,
            data=[product.to_response() for product in products],
        )


async def get_product_handler(product_id: str, tenant_id: str) -> ProductResponse:
    async with db_session() as session_ctx:
        product = await products_db.get_product_by_id(
            session=session_ctx.session, 
            product_id=product_id,
            tenant_id=tenant_id
        )
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    return product.to_response()


async def update_product_handler(
    product_id: str, 
    request: UpdateProductRequest,
    tenant_id: str
) -> ProductResponse:
    async with db_session() as session_ctx:
        product = await products_db.update_product(
            db=session_ctx.session, 
            product_id=product_id, 
            request=request,
            tenant_id=tenant_id
        )
    return product.to_response()
