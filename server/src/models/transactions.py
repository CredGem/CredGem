from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field
from sqlalchemy import JSON
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import DBModel, DBModelResponse, PaginatedResponse


class TransactionType(str, Enum):
    DEPOSIT = "deposit"  # add credit to wallet (including refunds)
    DEBIT = "debit"  # remove credits from wallet
    HOLD = "hold"  # reserve credits
    RELEASE = "release"  # release credits
    ADJUST = "adjust"  # adjust wallet balance


class HoldStatus(str, Enum):
    HELD = "held"
    USED = "used"  # Used by a debit
    RELEASED = "released"  # Explicitly released without use
    EXPIRED = "expired"  # Expired without use


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class BalanceSnapshot(BaseModel):
    available: float
    held: float
    spent: float
    overall_spent: float


class TransactionRequestBase(BaseModel):
    type: TransactionType
    credit_type_id: str
    description: str
    external_id: Optional[str] = Field(
        default=None, description="External transaction id"
    )
    payload: Any
    issuer: str
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Context for the transaction"
    )


class RequestPayloadBase(BaseModel):
    type: TransactionType


class DepositTransactionRequestPayload(RequestPayloadBase):
    type: Literal["deposit"] = Field(default="deposit")
    amount: float = Field(gt=0, description="Amount to deposit")


class DepositTransactionRequest(TransactionRequestBase):
    type: Literal["deposit"] = Field(default="deposit")
    payload: DepositTransactionRequestPayload


class SubscriptionDepositRequest(DepositTransactionRequest):
    subscription_id: str = Field(description="Id of the subscription to deposit for")


class DebitTransactionRequestPayload(RequestPayloadBase):
    type: Literal["debit"] = Field(default="debit")
    amount: float = Field(gt=0, description="Amount to debit")
    hold_transaction_id: Optional[str] = Field(
        default=None, description="Id of the hold transaction to debit"
    )


class DebitTransactionRequest(TransactionRequestBase):
    type: Literal["debit"] = Field(default="debit")
    payload: DebitTransactionRequestPayload


class HoldTransactionRequestPayload(RequestPayloadBase):
    type: Literal["hold"] = Field(default="hold")
    amount: float = Field(gt=0, description="Amount to hold")


class HoldTransactionRequest(TransactionRequestBase):
    type: Literal["hold"] = Field(default="hold")
    payload: HoldTransactionRequestPayload


class ReleaseTransactionRequestPayload(RequestPayloadBase):
    type: Literal["release"] = Field(default="release")
    hold_transaction_id: str = Field(
        description="Id of the hold transaction to release"
    )


class ReleaseTransactionRequest(TransactionRequestBase):
    type: Literal["release"] = Field(default="release")
    payload: ReleaseTransactionRequestPayload


class AdjustTransactionRequestPayload(RequestPayloadBase):
    type: Literal["adjust"] = Field(default="adjust")
    amount: float = Field(description="Amount to adjust")
    reset_spent: bool = False


class AdjustTransactionRequest(TransactionRequestBase):
    type: Literal["adjust"] = Field(default="adjust")
    payload: AdjustTransactionRequestPayload


TransactionRequestPayload = Annotated[
    Union[
        DepositTransactionRequestPayload,
        DebitTransactionRequestPayload,
        HoldTransactionRequestPayload,
        ReleaseTransactionRequestPayload,
        AdjustTransactionRequestPayload,
    ],
    Field(discriminator="type"),
]


class TransactionResponse(DBModelResponse):
    type: TransactionType
    credit_type_id: str
    description: str
    context: Optional[Dict[str, Any]]
    external_id: Optional[str]
    payload: Any
    balance_snapshot: Optional[dict] = None
    subscription_id: Optional[str] = None
    hold_status: Optional[HoldStatus] = None
    wallet_id: str
    status: TransactionStatus


class TransactionDBModel(DBModel):
    __tablename__ = "transactions"

    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType))
    external_id: Mapped[Optional[str]] = mapped_column(
        String, index=True, unique=True, nullable=True
    )
    wallet_id: Mapped[str] = mapped_column(String, index=True)
    credit_type_id: Mapped[str] = mapped_column(String, index=True)
    issuer: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default={})
    payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON
    )  # TransactionRequestPayload will be stored as JSON
    hold_status: Mapped[Optional[HoldStatus]] = mapped_column(
        SQLEnum(HoldStatus), nullable=True
    )
    status: Mapped[TransactionStatus] = mapped_column(SQLEnum(TransactionStatus))
    balance_snapshot: Mapped[Optional[Dict[str, float]]] = mapped_column(
        JSON, nullable=True
    )  # BalanceSnapshot as JSON
    subscription_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    def to_response(self) -> TransactionResponse:
        return TransactionResponse(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            type=self.type,
            credit_type_id=self.credit_type_id,
            description=self.description,
            context=self.context,
            external_id=self.external_id,
            payload=self.payload,
            balance_snapshot=self.balance_snapshot,
            subscription_id=self.subscription_id,
            hold_status=self.hold_status,
            wallet_id=self.wallet_id,
            status=self.status,
        )


class PaginatedTransactionResponse(PaginatedResponse):
    data: List[TransactionResponse]


class PaginatedTransactionDBModel(PaginatedResponse):
    data: List[TransactionDBModel]
