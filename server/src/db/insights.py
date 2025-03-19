from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Float, String, and_, case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import CreditType, TransactionDBModel, Wallet
from src.models.Insights import (
    CreditUsageAggregationResult,
    CreditUsageTimeSeriesAggregationResult,
    TimeGranularity,
    TrendingWalletAggregationResult,
    WalletActivityAggregationResult,
)


async def get_wallet_activity_aggregation(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    granularity: TimeGranularity,
    tenant_id: str,
    context: Optional[Dict[str, str]] = None,
) -> List[WalletActivityAggregationResult]:
    date_grouping = get_date_grouping_by_granularity(granularity)

    query = (
        select(
            date_grouping.label("timestamp"),
            TransactionDBModel.wallet_id,
            Wallet.name.label("wallet_name"),
            func.count().label("total_transactions"),
            func.count(
                case(
                    (TransactionDBModel.type == "DEPOSIT", 1),
                    else_=0,
                )
            ).label("total_deposits"),
            func.count(
                case(
                    (TransactionDBModel.type == "DEBIT", 1),
                    else_=0,
                )
            ).label("total_debits"),
            func.count(
                case(
                    (TransactionDBModel.type == "HOLD", 1),
                    else_=0,
                )
            ).label("total_holds"),
            func.count(
                case(
                    (TransactionDBModel.type == "ADJUST", 1),
                    else_=0,
                )
            ).label("total_adjustments"),
            func.sum(
                case(
                    (TransactionDBModel.type == "RELEASE", 1),
                    else_=0,
                )
            ).label("total_releases"),
        )
        .select_from(TransactionDBModel)
        .join(Wallet, Wallet.id == TransactionDBModel.wallet_id)
        .where(
            and_(
                TransactionDBModel.created_at.between(start_date, end_date),
                TransactionDBModel.tenant_id == tenant_id,
                *(
                    TransactionDBModel.context[key].as_string() == value
                    for key, value in (context or {}).items()
                ),
            )
        )
        .group_by(date_grouping, TransactionDBModel.wallet_id, Wallet.name)
        .order_by("timestamp", TransactionDBModel.wallet_id)
    )

    results = (await session.execute(query)).all()
    return [WalletActivityAggregationResult(**result._asdict()) for result in results]


async def get_trending_wallets(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    tenant_id: str,
    limit: int,
) -> List[TrendingWalletAggregationResult]:
    query = (
        select(
            TransactionDBModel.wallet_id,
            Wallet.name.label("wallet_name"),
            func.count().label("transaction_count"),
        )
        .select_from(TransactionDBModel)
        .join(Wallet, Wallet.id == TransactionDBModel.wallet_id)
        .where(
            and_(
                TransactionDBModel.created_at.between(start_date, end_date),
                TransactionDBModel.tenant_id == tenant_id
            )
        )
        .group_by(TransactionDBModel.wallet_id, Wallet.name)
        .order_by(desc("transaction_count"), TransactionDBModel.wallet_id)
        .limit(limit)
    )

    results = (await session.execute(query)).all()
    return [TrendingWalletAggregationResult(**result._asdict()) for result in results]


async def get_credit_usage_aggregation(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    tenant_id: str,
) -> List[CreditUsageAggregationResult]:
    """
    SQLAlchemy version of credit usage aggregation
    """
    query = (
        select(
            TransactionDBModel.credit_type_id,
            CreditType.name.label("credit_type_name"),
            func.sum(
                case(
                    (
                        TransactionDBModel.type == "DEBIT",
                        func.cast(
                            func.cast(TransactionDBModel.payload["amount"], String),
                            Float,
                        ),
                    ),
                    else_=0,
                )
            ).label("debits_amount"),
            func.count().label("transaction_count"),
        )
        .select_from(TransactionDBModel)
        .outerjoin(CreditType, CreditType.id == TransactionDBModel.credit_type_id)
        .where(
            and_(
                TransactionDBModel.type == "DEBIT",
                TransactionDBModel.created_at.between(start_date, end_date),
                TransactionDBModel.tenant_id == tenant_id
            )
        )
        .group_by(TransactionDBModel.credit_type_id, CreditType.name)
        .order_by(desc("debits_amount"), TransactionDBModel.credit_type_id)
    )

    results = (await session.execute(query)).all()
    return [CreditUsageAggregationResult(**result._asdict()) for result in results]


async def get_credit_usage_timeseries_aggregation(
    session: AsyncSession,
    start_date: datetime,
    end_date: datetime,
    granularity: TimeGranularity,
    tenant_id: str,
) -> List[CreditUsageTimeSeriesAggregationResult]:
    date_grouping = get_date_grouping_by_granularity(granularity)

    query = (
        select(
            date_grouping.label("timestamp"),
            TransactionDBModel.credit_type_id,
            CreditType.name.label("credit_type_name"),
            func.count().label("transaction_count"),
            func.sum(
                case(
                    (
                        TransactionDBModel.type == "DEBIT",
                        func.cast(
                            func.cast(TransactionDBModel.payload["amount"], String),
                            Float,
                        ),
                    ),
                    else_=0,
                )
            ).label("debits_amount"),
        )
        .select_from(TransactionDBModel)
        .outerjoin(CreditType, CreditType.id == TransactionDBModel.credit_type_id)
        .where(
            and_(
                TransactionDBModel.created_at.between(start_date, end_date),
                TransactionDBModel.tenant_id == tenant_id
            )
        )
        .group_by(date_grouping, TransactionDBModel.credit_type_id, CreditType.name)
        .order_by(date_grouping, TransactionDBModel.credit_type_id)
    )

    results = (await session.execute(query)).all()
    return [
        CreditUsageTimeSeriesAggregationResult(**result._asdict()) for result in results
    ]


def get_date_grouping_by_granularity(granularity: TimeGranularity):
    """
    Returns the appropriate SQLAlchemy date extraction functions
    for the given granularity
    """
    if granularity == TimeGranularity.DAY:
        return func.date_trunc("day", TransactionDBModel.created_at)
    elif granularity == TimeGranularity.WEEK:
        return func.date_trunc("week", TransactionDBModel.created_at)
    else:  # MONTH
        return func.date_trunc("month", TransactionDBModel.created_at)
