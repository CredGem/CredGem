from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel


class TimeGranularity(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class GeneralInsightsResponse(BaseModel):
    total_transactions: int
    total_deposits: int
    total_debits: int
    total_holds: int
    total_releases: int
    total_adjustments: int
    total_wallets: int
    total_credit_types: int


class InsightTimeSeriesBaseResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    granularity: TimeGranularity
    points: List[BaseModel]


class WalletActivityAggregationResult(BaseModel):
    timestamp: datetime
    wallet_id: str
    wallet_name: str
    total_transactions: int
    total_deposits: float = 0
    total_debits: float = 0
    total_holds: float = 0
    total_releases: float = 0
    total_adjustments: float = 0


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


class WalletActivityResponse(InsightTimeSeriesBaseResponse):
    points: List[WalletActivityPoint]


class CreditUsagePoint(BaseModel):
    timestamp: datetime
    wallet_id: str
    wallet_name: str
    total_debits: float = 0
    total_holds: float = 0
    total_releases: float = 0
    total_adjustments: float = 0


class CreditUsageAggregationResult(BaseModel):
    credit_type_id: str
    credit_type_name: str
    transaction_count: int
    debits_amount: float = 0


class CreditTypesUsage(BaseModel):
    credit_type_id: str
    credit_type_name: str
    debit_count: int = 0
    total_amount: float = 0


class CreditUsageTimeSeriesAggregationResult(BaseModel):
    timestamp: datetime
    credit_type_id: str
    credit_type_name: str
    transaction_count: int
    debits_amount: float = 0


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


class CreditUsageTimeSeriesResponse(InsightTimeSeriesBaseResponse):
    points: List[CreditUsageTimeSeriesPoint]


class TrendingWalletAggregationResult(BaseModel):
    wallet_id: str
    transaction_count: int
    wallet_name: str
