from fastapi import APIRouter, Depends, status

from src.models.base import PaginationRequest
from src.models.products import (
    CreateProductRequest,
    PaginatedProductResponse,
    ProductResponse,
    UpdateProductRequest,
)
from src.services import products_service
from src.utils.auth import AuthContext, get_auth_context

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "/",
    description="Create a new product",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    request: CreateProductRequest,
    auth: AuthContext = Depends(get_auth_context)
) -> ProductResponse:
    return await products_service.create_product_handler(
        request=request,
        tenant_id=auth.tenant_id,
        user_id=auth.user_id
    )


@router.get(
    "/",
    response_model=PaginatedProductResponse,
    description="Get all products",
)
async def get_products(
    pagination: PaginationRequest = Depends(),
    auth: AuthContext = Depends(get_auth_context)
) -> PaginatedProductResponse:
    return await products_service.get_products_handler(
        pagination_request=pagination,
        tenant_id=auth.tenant_id
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    description="Get a product by its ID",
)
async def get_product(
    product_id: str,
    auth: AuthContext = Depends(get_auth_context)
) -> ProductResponse:
    return await products_service.get_product_handler(
        product_id=product_id,
        tenant_id=auth.tenant_id
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    description="Update a product by its ID",
)
async def update_product(
    product_id: str,
    request: UpdateProductRequest,
    auth: AuthContext = Depends(get_auth_context)
) -> ProductResponse:
    return await products_service.update_product_handler(
        product_id=product_id,
        request=request,
        tenant_id=auth.tenant_id
    )
