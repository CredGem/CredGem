from fastapi import APIRouter, Depends, status

from src.models.base import PaginationRequest
from src.models.products import (
    CreateProductRequest,
    PaginatedProductResponse,
    ProductResponse,
    UpdateProductRequest,
)
from src.services import products_service
from src.utils.dependencies import get_pagination

router = APIRouter(prefix="/products", tags=["products"])


@router.post(
    "/",
    description="Create a new product",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    request: CreateProductRequest,
) -> ProductResponse:
    return await products_service.create_product_handler(request=request)


@router.get(
    "/",
    response_model=PaginatedProductResponse,
    description="Get all products",
)
async def get_products(
    pagination_request: PaginationRequest = Depends(get_pagination),
) -> PaginatedProductResponse:
    return await products_service.get_products_handler(
        pagination_request=pagination_request,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    description="Get a product by its ID",
)
async def get_product(product_id: str) -> ProductResponse:
    return await products_service.get_product_handler(product_id=product_id)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    description="Update a product by its ID",
)
async def update_product(
    product_id: str, request: UpdateProductRequest
) -> ProductResponse:
    return await products_service.update_product_handler(
        product_id=product_id, request=request
    )


@router.delete(
    "/{product_id}",
    description="Delete a product by its ID",
)
async def delete_product(product_id: str) -> None:
    return await products_service.delete_product_handler(product_id=product_id)
