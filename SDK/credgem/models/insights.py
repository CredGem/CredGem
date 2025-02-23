from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List


class TimeGranularity(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class WalletActivityPoint:
    timestamp: datetime
    wallet_id: str
    wallet_name: str
    total_transactions: int
    total_deposits: float = 0
    total_debits: float = 0
    total_holds: float = 0
    total_releases: float = 0
    total_adjustments: float = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WalletActivityPoint":
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            wallet_id=data["wallet_id"],
            wallet_name=data["wallet_name"],
            total_transactions=data["total_transactions"],
            total_deposits=data["total_deposits"],
            total_debits=data["total_debits"],
            total_holds=data["total_holds"],
            total_releases=data["total_releases"],
            total_adjustments=data["total_adjustments"],
        )


@dataclass
class WalletActivityResponse:
    start_date: datetime
    end_date: datetime
    granularity: TimeGranularity
    points: List[WalletActivityPoint]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WalletActivityResponse":
        return cls(
            start_date=datetime.fromisoformat(data["start_date"]),
            end_date=datetime.fromisoformat(data["end_date"]),
            granularity=TimeGranularity(data["granularity"]),
            points=[WalletActivityPoint.from_dict(point) for point in data["points"]],
        )


@dataclass
class CreditUsagePoint:
    timestamp: datetime
    wallet_id: str
    wallet_name: str
    total_debits: float = 0
    total_holds: float = 0
    total_releases: float = 0
    total_adjustments: float = 0


@dataclass
class CreditTypesUsage:
    credit_type_id: str
    credit_type_name: str
    debit_count: int = 0
    total_amount: float = 0


@dataclass
class CreditUsageResponse:
    credit_type_id: str
    credit_type_name: str
    transaction_count: int
    debits_amount: float = 0


@dataclass
class CreditUsageTimeSeriesPoint:
    timestamp: datetime
    credit_type_id: str
    credit_type_name: str
    transaction_count: int
    debits_amount: float = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreditUsageTimeSeriesPoint":
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            credit_type_id=data["credit_type_id"],
            credit_type_name=data["credit_type_name"],
            transaction_count=data["transaction_count"],
            debits_amount=data["debits_amount"],
        )


@dataclass
class CreditUsageTimeSeriesResponse:
    start_date: datetime
    end_date: datetime
    granularity: TimeGranularity
    points: List[CreditUsageTimeSeriesPoint]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreditUsageTimeSeriesResponse":
        return cls(
            start_date=datetime.fromisoformat(data["start_date"]),
            end_date=datetime.fromisoformat(data["end_date"]),
            granularity=TimeGranularity(data["granularity"]),
            points=[
                CreditUsageTimeSeriesPoint.from_dict(point) for point in data["points"]
            ],
        )
