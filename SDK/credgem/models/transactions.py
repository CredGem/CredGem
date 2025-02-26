from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Literal, Optional


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    DEBIT = "debit"
    HOLD = "hold"
    RELEASE = "release"
    ADJUST = "adjust"


class HoldStatus(str, Enum):
    HELD = "held"
    USED = "used"
    RELEASED = "released"
    EXPIRED = "expired"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(kw_only=True)
class TransactionBase:
    wallet_id: str
    credit_type_id: str
    description: str
    issuer: str
    external_id: Optional[str] = field(default=None)
    context: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass(kw_only=True)
class DepositRequest(TransactionBase):
    amount: float
    type: Literal[TransactionType.DEPOSIT] = field(default=TransactionType.DEPOSIT)


@dataclass(kw_only=True)
class DebitRequest(TransactionBase):
    amount: float
    type: Literal[TransactionType.DEBIT] = field(default=TransactionType.DEBIT)
    hold_transaction_id: Optional[str] = field(default=None)


@dataclass(kw_only=True)
class HoldRequest(TransactionBase):
    amount: float = field(default=0.0)
    type: Literal[TransactionType.HOLD] = field(default=TransactionType.HOLD)


@dataclass(kw_only=True)
class ReleaseRequest(TransactionBase):
    hold_transaction_id: str
    type: Literal[TransactionType.RELEASE] = field(default=TransactionType.RELEASE)


@dataclass(kw_only=True)
class AdjustRequest(TransactionBase):
    amount: float
    type: Literal[TransactionType.ADJUST] = field(default=TransactionType.ADJUST)
    reset_spent: bool = False


@dataclass(kw_only=True)
class TransactionResponse:
    id: str
    type: str
    credit_type_id: str
    wallet_id: str
    amount: float = field(default=0.0)
    description: Optional[str] = field(default=None)
    issuer: str = field(default="")
    context: Dict = field(default_factory=dict)
    created_at: str
    status: Optional[str] = field(default=None)
    hold_status: Optional[str] = field(default=None)
    payload: Optional[Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransactionResponse":
        # Extract amount from payload if present
        payload = data.get("payload", {})
        amount = float(payload.get("amount", 0)) if isinstance(payload, dict) else 0.0

        return cls(
            id=data["id"],
            type=data.get("type", ""),
            credit_type_id=data["credit_type_id"],
            wallet_id=data.get("wallet_id", ""),
            amount=amount,
            description=data.get("description"),
            issuer=data.get("issuer", ""),
            context=data.get("context", {}),
            created_at=data["created_at"],
            status=data.get("status"),
            hold_status=data.get("hold_status"),
            payload=payload,
        )
