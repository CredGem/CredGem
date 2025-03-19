from typing import List

from fastapi import HTTPException

from src.db import credit_types as credit_types_db
from src.models.credit_types import (
    CreateCreditTypeRequest,
    CreditTypeResponse,
    UpdateCreditTypeRequest,
)
from src.utils.ctx_managers import db_session


async def get_credit_type(credit_type_id: str, tenant_id: str) -> CreditTypeResponse:
    async with db_session(read_only=True) as session_ctx:
        credit_type = await credit_types_db.get_credit_type(
            db=session_ctx.session, 
            credit_type_id=credit_type_id,
            tenant_id=tenant_id
        )
        if not credit_type:
            raise HTTPException(status_code=404, detail="Credit type not found")
    return credit_type.to_response()


async def get_credit_types(tenant_id: str) -> List[CreditTypeResponse]:
    async with db_session(read_only=True) as session_ctx:
        credit_types = await credit_types_db.get_credit_types(
            db=session_ctx.session,
            tenant_id=tenant_id
        )
    return [credit_type.to_response() for credit_type in credit_types]


async def create_credit_type(
    credit_type_request: CreateCreditTypeRequest,
    tenant_id: str,
    user_id: str,
) -> CreditTypeResponse:
    async with db_session() as session_ctx:
        result = await credit_types_db.create_credit_type(
            db=session_ctx.session, 
            credit_type_request=credit_type_request,
            tenant_id=tenant_id,
            user_id=user_id
        )
        session_ctx.add_to_refresh([result])
    return result.to_response()


async def update_credit_type(
    credit_type_request: UpdateCreditTypeRequest, 
    credit_type_id: str,
    tenant_id: str
) -> CreditTypeResponse:
    async with db_session() as session_ctx:
        result = await credit_types_db.update_credit_type(
            db=session_ctx.session,
            credit_type_request=credit_type_request,
            credit_type_id=credit_type_id,
            tenant_id=tenant_id
        )
        if not result:
            raise HTTPException(status_code=404, detail="Credit type not found")
        session_ctx.add_to_refresh([result])
    return result.to_response()


async def delete_credit_type(credit_type_id: str, tenant_id: str) -> None:
    async with db_session() as session_ctx:
        deleted = await credit_types_db.delete_credit_type(
            db=session_ctx.session, 
            credit_type_id=credit_type_id,
            tenant_id=tenant_id
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="Credit type not found")
