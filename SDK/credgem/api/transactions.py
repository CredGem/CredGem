from typing import Dict, List, Optional, Any, Union, Literal
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
    amount: float = Field(gt=0, description="Amount to deposit")


class DebitRequest(TransactionBase):
    type: Literal[TransactionType.DEBIT] = Field(default=TransactionType.DEBIT)
    amount: float = Field(gt=0, description="Amount to debit")
    hold_external_transaction_id: Optional[str] = Field(
        default=None, description="Id of the hold transaction to debit"
    )


class HoldRequest(TransactionBase):
    type: Literal[TransactionType.HOLD] = Field(default=TransactionType.HOLD)
    amount: float = Field(gt=0, description="Amount to hold")


class ReleaseRequest(TransactionBase):
    type: Literal[TransactionType.RELEASE] = Field(default=TransactionType.RELEASE)
    hold_external_transaction_id: str = Field(description="Id of the hold transaction to release")


class AdjustRequest(TransactionBase):
    type: Literal[TransactionType.ADJUST] = Field(default=TransactionType.ADJUST)
    amount: float = Field(description="Amount to adjust")
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
        amount: float,
        credit_type_id: str,
        description: str | None = None,
        issuer: str | None = None,
        context: Optional[Dict] = None,
        external_transaction_id: str | None = None,

    ) -> TransactionResponse:
        """Create a hold on credits in a wallet."""
        payload = {
            "payload":{"type":"hold","amount": str(amount)},
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "context": context
        }
        if external_transaction_id:
            payload["external_transaction_id"] = external_transaction_id
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return await self._post(
            f"/wallets/{wallet_id}/hold",
            payload,
            TransactionResponse,
        )
    
    async def debit(
        self,
        wallet_id: str,
        amount: float,
        credit_type_id: str,
        description: str | None = None,
        issuer: str | None = None,
        external_transaction_id: str | None = None,
        hold_transaction_id: str | None = None,
            context: Optional[Dict] = None,
    ) -> TransactionResponse:
        """Debit credits from a wallet."""
        payload = {
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "context": context,
            "payload":{
                "amount":amount,
            },
            "external_transaction_id": external_transaction_id,
        }
        if hold_transaction_id:
            payload["payload"]["hold_transaction_id"] = hold_transaction_id
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return await self._post(
            f"/wallets/{wallet_id}/debit",
            payload,
            TransactionResponse,
        )
    
    async def release(
        self,
        wallet_id: str,
        hold_transaction_id: str,
        credit_type_id: str,
        description: str,
        issuer: str,
        external_transaction_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> TransactionResponse:
        """Release a hold on credits."""
        data = {
            "type": "release",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "external_transaction_id":external_transaction_id,
            "payload": {
                "type": "release",
                "hold_transaction_id": hold_transaction_id
            },
            "context": context or {}
        }
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
        amount: float,
        credit_type_id: str,
        description: str,
        issuer: str,
        external_transaction_id: Optional[str] = None,
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
        if idempotency_key:
            data["idempotency_key"] = idempotency_key
        
        return await self._post(
            f"/wallets/{wallet_id}/deposit",
            json=data,
            response_model=TransactionResponse
        )
    
    async def get(self, external_transaction_id: str) -> TransactionResponse:
        """Get a transaction by ID"""
        return await self._get(f"/transactions/{external_transaction_id}", response_model=TransactionResponse)
    
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