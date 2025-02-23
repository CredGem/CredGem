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


@dataclass
class BalanceSnapshot:
    available: float
    held: float
    spent: float
    overall_spent: float


@dataclass
class TransactionBase:
    wallet_id: str
    credit_type_id: str
    description: str
    issuer: str
    idempotency_key: Optional[str] = None
    context: Optional[Dict[str, Any]] = field(default_factory=dict)


class DepositRequest(TransactionBase):
    amount: float
    type: Literal[TransactionType.DEPOSIT] = TransactionType.DEPOSIT


class DebitRequest(TransactionBase):
    amount: float
    type: Literal[TransactionType.DEBIT] = TransactionType.DEBIT
    hold_external_transaction_id: Optional[str] = None


class HoldRequest(TransactionBase):
    type: Literal[TransactionType.HOLD] = TransactionType.HOLD
    amount: float


class ReleaseRequest(TransactionBase):
    type: Literal[TransactionType.RELEASE] = TransactionType.RELEASE
    hold_external_transaction_id: str


class AdjustRequest(TransactionBase):
    type: Literal[TransactionType.ADJUST] = TransactionType.ADJUST
    amount: float
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
