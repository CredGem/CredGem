from datetime import datetime
from typing import Dict, List, Optional

from src.db import insights as insights_db
from src.models.Insights import (
    CreditUsageResponse,
    CreditUsageTimeSeriesPoint,
    CreditUsageTimeSeriesResponse,
    TimeGranularity,
    TrendingWalletAggregationResult,
    WalletActivityPoint,
    WalletActivityResponse,
)
from src.utils.ctx_managers import db_session


async def get_wallet_activity(
    start_date: datetime,
    end_date: datetime,
    granularity: TimeGranularity,
    context: Optional[Dict[str, str]] = None,
) -> WalletActivityResponse:
    async with db_session() as session_ctx:
        session = session_ctx.session
        results = await insights_db.get_wallet_activity_aggregation(
            session=session,
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
            context=context,
        )

    activity_points = []
    for result in results:
        activity_points.append(
            WalletActivityPoint(
                timestamp=result.timestamp,
                wallet_id=result.wallet_id,
                wallet_name=result.wallet_name,
                total_transactions=result.total_transactions,
                total_deposits=result.total_deposits,
                total_debits=result.total_debits,
                total_holds=result.total_holds,
                total_releases=result.total_releases,
                total_adjustments=result.total_adjustments,
            )
        )

    return WalletActivityResponse(
        granularity=granularity,
        start_date=start_date,
        end_date=end_date,
        points=activity_points,
    )


async def get_trending_wallets(
    start_date: datetime,
    end_date: datetime,
    limit: int,
) -> List[TrendingWalletAggregationResult]:
    async with db_session() as session_ctx:
        session = session_ctx.session
        results = await insights_db.get_trending_wallets(
            session=session,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

    return results


async def get_credit_usage(
    start_date: datetime,
    end_date: datetime,
) -> List[CreditUsageResponse]:
    async with db_session() as session_ctx:
        session = session_ctx.session
        results = await insights_db.get_credit_usage_aggregation(
            session=session,
            start_date=start_date,
            end_date=end_date,
        )

    return [
        CreditUsageResponse(
            credit_type_id=result.credit_type_id,
            credit_type_name=result.credit_type_name,
            transaction_count=result.transaction_count,
            debits_amount=result.debits_amount,
        )
        for result in results
    ]


async def get_credit_usage_timeseries(
    start_date: datetime,
    end_date: datetime,
    granularity: TimeGranularity,
) -> CreditUsageTimeSeriesResponse:
    async with db_session() as session_ctx:
        session = session_ctx.session
        results = await insights_db.get_credit_usage_timeseries_aggregation(
            session=session,
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
        )

    points = [
        CreditUsageTimeSeriesPoint(
            timestamp=result.timestamp,
            credit_type_id=result.credit_type_id,
            credit_type_name=result.credit_type_name,
            transaction_count=result.transaction_count,
            debits_amount=result.debits_amount,
        )
        for result in results
    ]

    return CreditUsageTimeSeriesResponse(
        granularity=granularity,
        start_date=start_date,
        end_date=end_date,
        points=points,
    )
