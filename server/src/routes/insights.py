from typing import Dict, List

from fastapi import APIRouter, Depends, Query

from src.models.Insights import (
    CreditUsageResponse,
    CreditUsageTimeSeriesResponse,
    GeneralInsightsResponse,
    TimeGranularity,
    TrendingWalletAggregationResult,
    WalletActivityResponse,
)
from src.services import insights_service
from src.utils.dependencies import DateTimeRange, dict_parser, get_datetime_range

router = APIRouter(prefix="/insights")


@router.get("/general", response_model=GeneralInsightsResponse)
async def get_general_insights() -> GeneralInsightsResponse:
    """
    Get general insights including transaction counts, deposit counts etc.
    """
    return await insights_service.get_general_insights()


@router.get("/wallets/activity", response_model=WalletActivityResponse)
async def get_wallet_activity(
    date_range: DateTimeRange = Depends(get_datetime_range),
    granularity: TimeGranularity = TimeGranularity.DAY,
    context: Dict[str, str] = Depends(dict_parser("context")),
) -> WalletActivityResponse:
    return await insights_service.get_wallet_activity(
        start_date=date_range.start_date,
        end_date=date_range.end_date,
        granularity=granularity,
        context=context,
    )


@router.get("/wallets/trending", response_model=List[TrendingWalletAggregationResult])
async def get_trending_wallets(
    date_range: DateTimeRange = Depends(get_datetime_range),
    limit: int = Query(
        default=5, description="Number of trending wallets to return", ge=1, le=100
    ),
) -> List[TrendingWalletAggregationResult]:
    return await insights_service.get_trending_wallets(
        start_date=date_range.start_date,
        end_date=date_range.end_date,
        limit=limit,
    )


@router.get("/credits/usage-summary", response_model=List[CreditUsageResponse])
async def get_credit_usage(
    date_range: DateTimeRange = Depends(get_datetime_range),
) -> List[CreditUsageResponse]:
    return await insights_service.get_credit_usage(
        start_date=date_range.start_date,
        end_date=date_range.end_date,
    )


@router.get("/credits/usage-timeseries", response_model=CreditUsageTimeSeriesResponse)
async def get_credit_usage_timeseries(
    date_range: DateTimeRange = Depends(get_datetime_range),
    granularity: TimeGranularity = TimeGranularity.DAY,
) -> CreditUsageTimeSeriesResponse:
    return await insights_service.get_credit_usage_timeseries(
        start_date=date_range.start_date,
        end_date=date_range.end_date,
        granularity=granularity,
    )
