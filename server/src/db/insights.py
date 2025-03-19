from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Float, String, and_, case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import CreditType, TransactionDBModel, Wallet
from src.models.Insights import (
    CreditUsageAggregationResult,
    CreditUsageTimeSeriesAggregationResult,
    GeneralInsightsResponse,
    TimeGranularity,
    TrendingWalletAggregationResult,
    WalletActivityAggregationResult,
)


async def get_general_insights(
    session: AsyncSession,
) -> GeneralInsightsResponse:
    """
    Get general insights including transaction counts, deposit counts etc.
    """
    # Query for transaction statistics
    transaction_stats_query = select(
        func.count().label("total_transactions"),
        func.sum(
            case(
                (TransactionDBModel.type == "DEPOSIT", 1),
                else_=0,
            )
        ).label("total_deposits"),
        func.sum(
            case(
                (TransactionDBModel.type == "DEBIT", 1),
                else_=0,
            )
        ).label("total_debits"),
        func.sum(
            case(
                (TransactionDBModel.type == "HOLD", 1),
                else_=0,
            )
        ).label("total_holds"),
        func.sum(
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
    ).select_from(TransactionDBModel)

    # Get counts for wallets and credit types
    total_wallets = (await session.execute(select(func.count(Wallet.id)))).scalar() or 0
    total_credit_types = (
        await session.execute(select(func.count(CreditType.id)))
    ).scalar() or 0

    # Execute transaction query and build response
    results = (await session.execute(transaction_stats_query)).all()

    return GeneralInsightsResponse(
        total_transactions=results[0][0],
        total_deposits=results[0][1],
        total_debits=results[0][2],
        total_holds=results[0][3],
        total_adjustments=results[0][4],
        total_releases=results[0][5],
        total_wallets=total_wallets,
        total_credit_types=total_credit_types,
    )


async def get_wallet_activity_aggregation(
    session: AsyncSession,  # Add session parameter
    start_date: datetime,
    end_date: datetime,
    granularity: TimeGranularity,
    context: Optional[Dict[str, str]] = None,
) -> List[WalletActivityAggregationResult]:
    date_grouping = get_date_grouping_by_granularity(granularity)

    query = (
        select(
            date_grouping.label("timestamp"),
            TransactionDBModel.wallet_id,
            Wallet.name.label("wallet_name"),
            func.count().label("total_transactions"),
            func.sum(
                case(
                    (TransactionDBModel.type == "DEPOSIT", 1),
                    else_=0,
                )
            ).label("total_deposits"),
            func.sum(
                case(
                    (TransactionDBModel.type == "DEBIT", 1),
                    else_=0,
                )
            ).label("total_debits"),
            func.sum(
                case(
                    (TransactionDBModel.type == "HOLD", 1),
                    else_=0,
                )
            ).label("total_holds"),
            func.sum(
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
        .where(and_(TransactionDBModel.created_at.between(start_date, end_date)))
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
            TransactionDBModel.created_at.between(start_date, end_date),
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
