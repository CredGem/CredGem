from typing import List

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.credit_types import (
    CreateCreditTypeRequest,
    CreditTypeResponse,
    UpdateCreditTypeRequest,
)
from src.services import credit_types_service
from src.utils.ctx_managers import db_session
from src.utils.router import APIRouter
from src.utils.auth import AuthContext, get_auth_context

router = APIRouter(
    prefix="/credit-types",
    tags=["credit_types"],
)


@router.post(
    "/",
    description="Create a new credit type",
    response_model=CreditTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_credit_type(
    credit_type_request: CreateCreditTypeRequest,
    auth: AuthContext = Depends(get_auth_context)
) -> CreditTypeResponse:
    return await credit_types_service.create_credit_type(
        credit_type_request=credit_type_request,
        tenant_id=auth.tenant_id,
        user_id=auth.user_id
    )


@router.get(
    "/",
    description="Get all credit types",
    response_model=List[CreditTypeResponse],
)
async def get_credit_types(auth: AuthContext = Depends(get_auth_context)) -> List[CreditTypeResponse]:
    return await credit_types_service.get_credit_types(tenant_id=auth.tenant_id)


@router.get(
    "/{credit_type_id}",
    description="Get a specific credit type",
    response_model=CreditTypeResponse,
)
async def get_credit_type(
    credit_type_id: str,
    auth: AuthContext = Depends(get_auth_context)
):
    return await credit_types_service.get_credit_type(
        credit_type_id=credit_type_id,
        tenant_id=auth.tenant_id
    )


@router.put(
    "/{credit_type_id}",
    description="Update an existing credit type",
    response_model=CreditTypeResponse,
)
async def update_credit_type(
    credit_type_id: str,
    credit_type_request: UpdateCreditTypeRequest,
    auth: AuthContext = Depends(get_auth_context)
) -> CreditTypeResponse:
    return await credit_types_service.update_credit_type(
        credit_type_request=credit_type_request,
        credit_type_id=credit_type_id,
        tenant_id=auth.tenant_id
    )


@router.delete(
    "/{credit_type_id}",
    description="Delete a credit type",
)
async def delete_credit_type(
    credit_type_id: str,
    auth: AuthContext = Depends(get_auth_context)
) -> None:
    await credit_types_service.delete_credit_type(
        credit_type_id=credit_type_id,
        tenant_id=auth.tenant_id
    )
