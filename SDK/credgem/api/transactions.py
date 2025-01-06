from typing import Dict, List, Optional, Any, Union, Literal
from decimal import Decimal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from credgem.api.base import BaseAPI


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


class BalanceSnapshot(BaseModel):
    available: float
    held: float
    spent: float
    overall_spent: float


class TransactionBase(BaseModel):
    wallet_id: str
    credit_type_id: str
    description: str
    idempotency_key: Optional[str] = Field(default=None, description="Idempotency key")
    issuer: str
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Context for the transaction"
    )


class DepositRequest(TransactionBase):
    type: Literal[TransactionType.DEPOSIT] = Field(default=TransactionType.DEPOSIT)
    amount: Decimal = Field(gt=0, description="Amount to deposit")


class DebitRequest(TransactionBase):
    type: Literal[TransactionType.DEBIT] = Field(default=TransactionType.DEBIT)
    amount: Decimal = Field(gt=0, description="Amount to debit")
    hold_transaction_id: Optional[str] = Field(
        default=None, description="Id of the hold transaction to debit"
    )


class HoldRequest(TransactionBase):
    type: Literal[TransactionType.HOLD] = Field(default=TransactionType.HOLD)
    amount: Decimal = Field(gt=0, description="Amount to hold")


class ReleaseRequest(TransactionBase):
    type: Literal[TransactionType.RELEASE] = Field(default=TransactionType.RELEASE)
    hold_transaction_id: str = Field(description="Id of the hold transaction to release")


class AdjustRequest(TransactionBase):
    type: Literal[TransactionType.ADJUST] = Field(default=TransactionType.ADJUST)
    amount: Decimal = Field(description="Amount to adjust")
    reset_spent: bool = False


class TransactionResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    type: TransactionType
    credit_type_id: str
    description: str
    context: Optional[Dict[str, Any]]
    idempotency_key: str
    wallet_id: str
    issuer: str
    status: TransactionStatus
    hold_status: Optional[HoldStatus]
    balance_snapshot: Optional[BalanceSnapshot]


class PaginatedTransactionResponse(BaseModel):
    page: int
    page_size: int
    total_count: int
    data: List[TransactionResponse]


class TransactionsAPI(BaseAPI):
    async def deposit(
        self,
        wallet_id: str,
        amount: Decimal,
        credit_type_id: str,
        description: str,
        issuer: str,
        idempotency_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> TransactionResponse:
        """Create a deposit transaction"""
        data = DepositRequest(
            wallet_id=wallet_id,
            amount=amount,
            credit_type_id=credit_type_id,
            description=description,
            issuer=issuer,
            idempotency_key=idempotency_key,
            context=context,
        ).model_dump(exclude_none=True)
        return await self._post("/transactions/deposit", json=data, response_model=TransactionResponse)

    async def debit(
        self,
        wallet_id: str,
        amount: Decimal,
        credit_type_id: str,
        description: str,
        issuer: str,
        hold_transaction_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> TransactionResponse:
        """Create a debit transaction"""
        data = DebitRequest(
            wallet_id=wallet_id,
            amount=amount,
            credit_type_id=credit_type_id,
            description=description,
            issuer=issuer,
            hold_transaction_id=hold_transaction_id,
            idempotency_key=idempotency_key,
            context=context,
        ).model_dump(exclude_none=True)
        return await self._post("/transactions/debit", json=data, response_model=TransactionResponse)

    async def hold(
        self,
        wallet_id: str,
        amount: Decimal,
        credit_type_id: str,
        description: str,
        issuer: str,
        idempotency_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> TransactionResponse:
        """Create a hold transaction"""
        data = HoldRequest(
            wallet_id=wallet_id,
            amount=amount,
            credit_type_id=credit_type_id,
            description=description,
            issuer=issuer,
            idempotency_key=idempotency_key,
            context=context,
        ).model_dump(exclude_none=True)
        return await self._post("/transactions/hold", json=data, response_model=TransactionResponse)

    async def release(
        self,
        wallet_id: str,
        hold_transaction_id: str,
        credit_type_id: str,
        description: str,
        issuer: str,
        idempotency_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> TransactionResponse:
        """Release a hold transaction"""
        data = ReleaseRequest(
            wallet_id=wallet_id,
            hold_transaction_id=hold_transaction_id,
            credit_type_id=credit_type_id,
            description=description,
            issuer=issuer,
            idempotency_key=idempotency_key,
            context=context,
        ).model_dump(exclude_none=True)
        return await self._post("/transactions/release", json=data, response_model=TransactionResponse)

    async def adjust(
        self,
        wallet_id: str,
        amount: Decimal,
        credit_type_id: str,
        description: str,
        issuer: str,
        reset_spent: bool = False,
        idempotency_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> TransactionResponse:
        """Adjust wallet balance"""
        data = AdjustRequest(
            wallet_id=wallet_id,
            amount=amount,
            credit_type_id=credit_type_id,
            description=description,
            issuer=issuer,
            reset_spent=reset_spent,
            idempotency_key=idempotency_key,
            context=context,
        ).model_dump(exclude_none=True)
        return await self._post("/transactions/adjust", json=data, response_model=TransactionResponse)

    async def get(self, transaction_id: str) -> TransactionResponse:
        """Get a transaction by ID"""
        return await self._get(f"/transactions/{transaction_id}", response_model=TransactionResponse)

    async def list(
        self,
        wallet_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedTransactionResponse:
        """List transactions"""
        params = {"page": page, "page_size": page_size}
        if wallet_id:
            params["wallet_id"] = wallet_id
        return await self._get("/transactions", params=params, response_model=PaginatedTransactionResponse) 