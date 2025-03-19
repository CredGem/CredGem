from typing import Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends

from src.models.Insights import (
    CreditUsageResponse,
    CreditUsageTimeSeriesResponse,
    TimeGranularity,
    TrendingWalletAggregationResult,
    WalletActivityResponse,
)
from src.services import insights_service
from src.utils.auth import AuthContext, get_auth_context

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/wallet-activity", response_model=WalletActivityResponse)
async def get_wallet_activity(
    start_date: datetime,
    end_date: datetime,
    granularity: TimeGranularity,
    context: Optional[Dict[str, str]] = None,
    auth: AuthContext = Depends(get_auth_context)
):
    return await insights_service.get_wallet_activity(
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        tenant_id=auth.tenant_id,
        context=context
    )


@router.get("/trending-wallets", response_model=List[TrendingWalletAggregationResult])
async def get_trending_wallets(
    start_date: datetime,
    end_date: datetime,
    limit: int = 10,
    auth: AuthContext = Depends(get_auth_context)
):
    return await insights_service.get_trending_wallets(
        start_date=start_date,
        end_date=end_date,
        tenant_id=auth.tenant_id,
        limit=limit
    )


@router.get("/credit-usage", response_model=List[CreditUsageResponse])
async def get_credit_usage(
    start_date: datetime,
    end_date: datetime,
    auth: AuthContext = Depends(get_auth_context)
):
    return await insights_service.get_credit_usage(
        start_date=start_date,
        end_date=end_date,
        tenant_id=auth.tenant_id
    )


@router.get("/credit-usage-timeseries", response_model=CreditUsageTimeSeriesResponse)
async def get_credit_usage_timeseries(
    start_date: datetime,
    end_date: datetime,
    granularity: TimeGranularity,
    auth: AuthContext = Depends(get_auth_context)
):
    return await insights_service.get_credit_usage_timeseries(
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        tenant_id=auth.tenant_id
    )
