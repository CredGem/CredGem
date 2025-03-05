from datetime import datetime
from typing import Any, Dict, Optional

from credgem.api.base import BaseAPI
from credgem.models.insights import (
    CreditUsageTimeSeriesResponse,
    TimeGranularity,
    WalletActivityResponse,
)


class InsightsAPI(BaseAPI):
    async def get_wallet_activity(
        self,
        wallet_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: TimeGranularity = TimeGranularity.DAY,
    ) -> WalletActivityResponse:
        """Get activity insights for a specific wallet"""
        params: Dict[str, Any] = {"granularity": granularity}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        return await self._get(
            f"/insights/wallets/{wallet_id}/activity",
            params=params,
            response_model=WalletActivityResponse,
        )

    async def get_credit_usage(
        self,
        wallet_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: TimeGranularity = TimeGranularity.DAY,
    ) -> CreditUsageTimeSeriesResponse:
        """Get credit usage insights for a specific wallet"""
        params: Dict[str, Any] = {"granularity": granularity}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        return await self._get(
            f"/insights/wallets/{wallet_id}/credit-usage",
            params=params,
            response_model=CreditUsageTimeSeriesResponse,
        )

    async def get_system_credit_usage(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: TimeGranularity = TimeGranularity.DAY,
    ) -> CreditUsageTimeSeriesResponse:
        """Get system-wide credit usage insights"""
        params: Dict[str, Any] = {"granularity": granularity}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        return await self._get(
            "/insights/system/credit-usage",
            params=params,
            response_model=CreditUsageTimeSeriesResponse,
        )
