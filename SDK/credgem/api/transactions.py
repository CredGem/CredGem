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
    wallet_id: Optional[str] = None
    credit_type_id: str
    description: Optional[str] = None
    issuer: Optional[str] = None
    context: Dict = {}
    status: Optional[str] = None
    hold_status: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    balance_snapshot: Optional[Dict[str, float]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PaginatedTransactionResponse(BaseModel):
    page: int
    page_size: int
    total_count: int
    data: List[TransactionResponse]


class TransactionsAPI(BaseAPI):
    """API client for transaction operations."""
    
    async def hold(
        self,
        wallet_id: str,
        amount: Decimal,
        credit_type_id: str,
        description: str,
        issuer: str,
        transaction_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> TransactionResponse:
        """Create a hold on credits in a wallet."""
        data = {
            "type": "hold",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "payload": {
                "amount": float(amount)
            },
            "context": context or {}
        }
        if transaction_id:
            data["id"] = transaction_id
        if idempotency_key:
            data["idempotency_key"] = idempotency_key
        
        return await self._post(
            f"/wallets/{wallet_id}/hold",
            json=data,
            response_model=TransactionResponse
        )
    
    async def debit(
        self,
        wallet_id: str,
        amount: Decimal,
        credit_type_id: str,
        description: str,
        issuer: str,
        hold_transaction_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> TransactionResponse:
        """Debit credits from a wallet."""
        data = {
            "type": "debit",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "payload": {
                "type": "debit",
                "amount": float(amount)
            },
            "context": context or {}
        }
        if hold_transaction_id:
            data["payload"]["hold_transaction_id"] = hold_transaction_id
        if transaction_id:
            data["id"] = transaction_id
        if idempotency_key:
            data["idempotency_key"] = idempotency_key
        
        return await self._post(
            f"/wallets/{wallet_id}/debit",
            json=data,
            response_model=TransactionResponse
        )
    
    async def release(
        self,
        wallet_id: str,
        hold_transaction_id: str,
        credit_type_id: str,
        description: str,
        issuer: str,
        transaction_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> TransactionResponse:
        """Release a hold on credits."""
        data = {
            "type": "release",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "payload": {
                "type": "release",
                "hold_transaction_id": hold_transaction_id
            },
            "context": context or {}
        }
        if transaction_id:
            data["id"] = transaction_id
        if idempotency_key:
            data["idempotency_key"] = idempotency_key
        
        return await self._post(
            f"/wallets/{wallet_id}/release",
            json=data,
            response_model=TransactionResponse
        )
    
    async def deposit(
        self,
        wallet_id: str,
        amount: Decimal,
        credit_type_id: str,
        description: str,
        issuer: str,
        transaction_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> TransactionResponse:
        """Deposit credits into a wallet."""
        data = {
            "type": "deposit",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "payload": {
                "type": "deposit",
                "amount": float(amount)
            },
            "context": context or {}
        }
        if transaction_id:
            data["id"] = transaction_id
        if idempotency_key:
            data["idempotency_key"] = idempotency_key
        
        return await self._post(
            f"/wallets/{wallet_id}/deposit",
            json=data,
            response_model=TransactionResponse
        )
    
    async def get(self, transaction_id: str) -> TransactionResponse:
        """Get a transaction by ID"""
        return await self._get(f"/transactions/{transaction_id}", response_model=TransactionResponse)
    
    async def list(
        self,
        wallet_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> TransactionResponse:
        """List transactions"""
        params = {"page": page, "page_size": page_size}
        if wallet_id:
            params["wallet_id"] = wallet_id
        return await self._get("/transactions", params=params, response_model=TransactionResponse) 