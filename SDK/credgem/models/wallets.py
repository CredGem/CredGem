from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from credgem.models import PaginatedResponse


class WalletStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass(kw_only=True)
class WalletRequest:
    name: str
    description: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass(kw_only=True)
class WalletUpdateRequest:
    name: Optional[str] = None
    description: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class Balance:
    credit_type_id: str
    available: float
    held: float
    spent: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Balance":
        return cls(
            credit_type_id=data["credit_type_id"],
            available=float(data["available"]),
            held=float(data["held"]),
            spent=float(data["spent"]),
        )


@dataclass(kw_only=True)
class WalletResponse:
    id: str
    name: str
    created_at: str
    updated_at: str
    description: Optional[str] = field(default=None)
    context: Dict = field(default_factory=dict)
    balances: List[Balance] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WalletResponse":
        # Handle optional fields with defaults
        balances_data = data.get("balances", [])
        balances = [
            Balance.from_dict(b) if isinstance(b, dict) else b for b in balances_data
        ]

        return cls(
            id=data["id"],
            name=data["name"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            description=data.get("description"),
            context=data.get("context", {}),
            balances=balances,
        )

    def __post_init__(self):
        if self.balances and isinstance(self.balances[0], dict):
            object.__setattr__(
                self,
                "balances",
                [
                    Balance.from_dict(b) if isinstance(b, dict) else b
                    for b in self.balances
                ],
            )


class PaginatedWalletResponse(PaginatedResponse):
    data: List[WalletResponse]
