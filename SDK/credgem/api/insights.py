from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

from credgem.api.base import BaseAPI


class TimeGranularity(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class WalletActivityPoint(BaseModel):
    timestamp: datetime
    wallet_id: str
    wallet_name: str
    total_transactions: int
    total_deposits: float = 0
    total_debits: float = 0
    total_holds: float = 0
    total_releases: float = 0
    total_adjustments: float = 0


class WalletActivityResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    granularity: TimeGranularity
    points: List[WalletActivityPoint]


class CreditUsagePoint(BaseModel):
    timestamp: datetime
    wallet_id: str
    wallet_name: str
    total_debits: float = 0
    total_holds: float = 0
    total_releases: float = 0
    total_adjustments: float = 0


class CreditTypesUsage(BaseModel):
    credit_type_id: str
    credit_type_name: str
    debit_count: int = 0
    total_amount: float = 0


class CreditUsageResponse(BaseModel):
    credit_type_id: str
    credit_type_name: str
    transaction_count: int
    debits_amount: float = 0


class CreditUsageTimeSeriesPoint(BaseModel):
    timestamp: datetime
    credit_type_id: str
    credit_type_name: str
    transaction_count: int
    debits_amount: float = 0


class CreditUsageTimeSeriesResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    granularity: TimeGranularity
    points: List[CreditUsageTimeSeriesPoint]


class InsightsAPI(BaseAPI):
    async def get_wallet_activity(
        self,
        wallet_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: TimeGranularity = TimeGranularity.DAY,
    ) -> WalletActivityResponse:
        """Get activity insights for a specific wallet"""
        params = {"granularity": granularity}
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
        params = {"granularity": granularity}
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
        params = {"granularity": granularity}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        return await self._get(
            "/insights/system/credit-usage",
            params=params,
            response_model=CreditUsageTimeSeriesResponse,
        ) 