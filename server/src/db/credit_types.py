from typing import List
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.credit_types import (
    CreateCreditTypeRequest,
    CreditType,
    UpdateCreditTypeRequest,
)


async def get_credit_types(db: AsyncSession, tenant_id: str) -> List[CreditType]:
    query = select(CreditType).where(CreditType.tenant_id == tenant_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_credit_type(
    db: AsyncSession, 
    credit_type_request: CreateCreditTypeRequest,
    tenant_id: str,
    user_id: str
) -> CreditType:
    credit_type = CreditType(
        id=str(uuid4()),
        name=credit_type_request.name,
        description=credit_type_request.description,
        tenant_id=tenant_id,
        user_id=user_id
    )
    db.add(credit_type)
    return credit_type


async def update_credit_type(
    db: AsyncSession,
    credit_type_id: str,
    credit_type_request: UpdateCreditTypeRequest,
    tenant_id: str
) -> CreditType | None:
    credit_type = await db.execute(
        select(CreditType).where(
            CreditType.id == credit_type_id,
            CreditType.tenant_id == tenant_id
        )
    )
    credit_type = credit_type.scalar_one_or_none()
    if not credit_type:
        return None

    if credit_type_request.name:
        credit_type.name = credit_type_request.name
    if credit_type_request.description:
        credit_type.description = credit_type_request.description
    db.add(credit_type)
    return credit_type


async def delete_credit_type(db: AsyncSession, credit_type_id: str, tenant_id: str) -> bool:
    result = await db.execute(
        delete(CreditType).where(
            CreditType.id == credit_type_id,
            CreditType.tenant_id == tenant_id
        )
    )
    return result.rowcount > 0


async def get_credit_type(db: AsyncSession, credit_type_id: str, tenant_id: str) -> CreditType | None:
    result = await db.execute(
        select(CreditType).where(
            CreditType.id == credit_type_id,
            CreditType.tenant_id == tenant_id
        )
    )
    return result.scalar_one_or_none()
