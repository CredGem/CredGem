from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from .base import BaseAPI


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


@dataclass
class PaginatedTransactionResponse:
    page: int
    page_size: int
    total_count: int
    data: List[TransactionResponse]


class TransactionsAPI(BaseAPI):
    """API client for transaction operations."""

    async def hold(
        self,
        wallet_id: str,
        credit_type_id: str,
        amount: float,
        description: Optional[str] = None,
        issuer: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        external_transaction_id: Optional[str] = None,
    ) -> TransactionResponse:
        payload = {
            "type": "hold",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "context": context or {},
            "payload": {"type": "hold", "amount": amount},
        }
        if external_transaction_id:
            payload["external_transaction_id"] = external_transaction_id

        response = await self._post(
            f"/wallets/{wallet_id}/hold", json=payload, response_model=None
        )
        return TransactionResponse.from_dict(response)

    async def debit(
        self,
        wallet_id: str,
        credit_type_id: str,
        amount: float,
        description: Optional[str] = None,
        issuer: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        hold_transaction_id: Optional[str] = None,
        external_transaction_id: Optional[str] = None,
    ) -> TransactionResponse:
        payload = {
            "type": "debit",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "context": context or {},
            "payload": {
                "type": "debit",
                "amount": str(amount),
                "hold_external_transaction_id": hold_transaction_id
                if hold_transaction_id
                else None,
            },
        }
        if external_transaction_id:
            payload["external_transaction_id"] = external_transaction_id

        try:
            response = await self._post(
                f"/wallets/{wallet_id}/debit", json=payload, response_model=None
            )
            debit_response = TransactionResponse.from_dict(response)

            # If this was a debit with hold, release the hold
            if hold_transaction_id:
                await self.release(
                    wallet_id=wallet_id,
                    hold_transaction_id=hold_transaction_id,
                    credit_type_id=credit_type_id,
                    description=description,
                    issuer=issuer,
                    context=context,
                    external_transaction_id=f"release_{external_transaction_id}"
                    if external_transaction_id
                    else None,
                )

            return debit_response
        except Exception as e:
            if hold_transaction_id and "invalid hold" in str(e).lower():
                raise ValueError("Invalid hold transaction ID") from e
            raise

    async def release(
        self,
        wallet_id: str,
        hold_transaction_id: str,
        credit_type_id: str,
        description: str,
        issuer: str,
        context: Optional[Dict[str, Any]] = None,
        external_transaction_id: Optional[str] = None,
    ) -> TransactionResponse:
        """Release a hold on credits in a wallet."""
        payload = {
            "type": "release",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "context": context or {},
            "payload": {"type": "release", "hold_transaction_id": hold_transaction_id},
        }

        if external_transaction_id is not None:
            payload["external_transaction_id"] = external_transaction_id

        response = await self._post(
            f"/wallets/{wallet_id}/release",
            json=payload,
        )

        return TransactionResponse.from_dict(response)

    async def deposit(
        self,
        wallet_id: str,
        credit_type_id: str,
        amount: float,
        description: Optional[str] = None,
        issuer: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> TransactionResponse:
        payload = {
            "type": "deposit",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "context": context or {},
            "payload": {"type": "deposit", "amount": str(amount)},
        }

        response = await self._post(
            f"/wallets/{wallet_id}/deposit", json=payload, response_model=None
        )
        return TransactionResponse.from_dict(response)

    async def get(self, transaction_id: str) -> TransactionResponse:
        response = await self._get(
            f"/transactions/{transaction_id}", response_model=None
        )
        return TransactionResponse.from_dict(response)

    async def list(
        self,
        wallet_id: Optional[str] = None,
        external_transaction_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> List[TransactionResponse]:
        """List transactions with optional filtering."""
        params = {"page": page, "page_size": page_size}
        if wallet_id:
            params["wallet_id"] = wallet_id
        if external_transaction_id:
            params["external_transaction_id"] = external_transaction_id
        response = await self._get("/transactions", params=params)
        return [
            TransactionResponse.from_dict(item) for item in response.get("data", [])
        ]
