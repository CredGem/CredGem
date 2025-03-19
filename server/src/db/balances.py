from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.balances import BalanceDBModel


async def get_balance(
    db: AsyncSession, 
    wallet_id: str, 
    credit_type_id: str,
    tenant_id: str
) -> BalanceDBModel | None:
    query = select(BalanceDBModel).where(
        BalanceDBModel.wallet_id == wallet_id,
        BalanceDBModel.credit_type_id == credit_type_id,
        BalanceDBModel.tenant_id == tenant_id
    )
    result = await db.execute(query)
    return result.scalars().first()


async def deposit_balance(
    session: AsyncSession, 
    wallet_id: str, 
    credit_type_id: str, 
    amount: float,
    tenant_id: str,
    user_id: str
) -> BalanceDBModel:
    # Create upsert statement
    stmt = (
        insert(BalanceDBModel)
        .values(
            id=str(uuid4()),
            wallet_id=wallet_id,
            credit_type_id=credit_type_id,
            available=amount,
            held=0,
            spent=0,
            overall_spent=0,
            tenant_id=tenant_id,
            user_id=user_id
        )
        .on_conflict_do_update(
            index_elements=["wallet_id", "credit_type_id", "tenant_id"],
            set_=dict(available=BalanceDBModel.available + amount),
        )
        .returning(BalanceDBModel)
    )

    result = await session.execute(stmt)
    return result.scalar_one()


async def debit_balance(
    session: AsyncSession,
    wallet_id: str,
    credit_type_id: str,
    amount: float,
    held_amount: float,
    spent: float,
    tenant_id: str
) -> BalanceDBModel | None:
    stmt = (
        update(BalanceDBModel)
        .where(
            BalanceDBModel.wallet_id == wallet_id,
            BalanceDBModel.credit_type_id == credit_type_id,
            BalanceDBModel.tenant_id == tenant_id
        )
        .values(
            available=BalanceDBModel.available - amount,
            held=BalanceDBModel.held - held_amount,
            spent=BalanceDBModel.spent + spent,
            overall_spent=BalanceDBModel.overall_spent + spent,
        )
        .returning(BalanceDBModel)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def hold_balance(
    session: AsyncSession, 
    wallet_id: str, 
    credit_type_id: str, 
    amount: float,
    tenant_id: str
) -> BalanceDBModel | None:
    stmt = (
        update(BalanceDBModel)
        .where(
            BalanceDBModel.wallet_id == wallet_id,
            BalanceDBModel.credit_type_id == credit_type_id,
            BalanceDBModel.tenant_id == tenant_id
        )
        .values(
            held=BalanceDBModel.held + amount,
            available=BalanceDBModel.available - amount,
        )
        .returning(BalanceDBModel)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def release_balance(
    session: AsyncSession, 
    wallet_id: str, 
    credit_type_id: str, 
    amount: float,
    tenant_id: str,
    user_id: str
) -> BalanceDBModel | None:
    stmt = (
        insert(BalanceDBModel)
        .values(
            id=str(uuid4()),
            wallet_id=wallet_id,
            credit_type_id=credit_type_id,
            tenant_id=tenant_id,
            user_id=user_id
        )
        .on_conflict_do_update(
            index_elements=["wallet_id", "credit_type_id", "tenant_id"],
            set_=dict(
                held=BalanceDBModel.held - amount,
                available=BalanceDBModel.available + amount,
            ),
        )
        .returning(BalanceDBModel)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def adjust_balance(
    session: AsyncSession,
    wallet_id: str,
    credit_type_id: str,
    amount: float,
    tenant_id: str,
    reset_spent: bool = False,
) -> BalanceDBModel | None:
    stmt = (
        update(BalanceDBModel)
        .where(
            BalanceDBModel.wallet_id == wallet_id,
            BalanceDBModel.credit_type_id == credit_type_id,
            BalanceDBModel.tenant_id == tenant_id
        )
        .values(
            available=amount,
            held=0,
            spent=0 if reset_spent else BalanceDBModel.spent,
        )
        .returning(BalanceDBModel)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
