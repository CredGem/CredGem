from enum import Enum
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import String, inspect
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.balances import BalanceDBModel, BalanceResponse
from src.models.base import DBModel, DBModelResponse, PaginatedResponse


class WalletStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class WalletResponse(DBModelResponse):
    name: str
    context: dict
    balances: List[BalanceResponse]
    status: WalletStatus


class Wallet(DBModel):
    __tablename__ = "wallets"

    name: Mapped[str] = mapped_column(String, nullable=False)  # type hint for name
    context: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default={}
    )  # type hint for context
    status: Mapped[WalletStatus] = mapped_column(
        SQLAlchemyEnum(WalletStatus), nullable=False, default=WalletStatus.ACTIVE
    )

    _balances: Mapped[List[BalanceDBModel]] = relationship(
        "BalanceDBModel", back_populates="wallet"
    )

    @property
    def balances(self) -> List[BalanceDBModel]:
        inspector = inspect(self)
        balances_loaded = "_balances" not in inspector.unloaded
        return self._balances if balances_loaded else []

    def __repr__(self):
        return f"Wallet(id='{self.id}', name='{self.name}', context={self.context})"

    def to_response(self) -> WalletResponse:
        return WalletResponse(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            name=self.name,
            context=self.context,
            status=self.status,
            balances=[balance.to_response() for balance in self.balances],
        )


class CreateWalletRequest(BaseModel):
    name: str
    context: dict = {}


class UpdateWalletRequest(BaseModel):
    name: Optional[str] = None
    context: Optional[dict] = None


class PaginatedWalletResponse(PaginatedResponse):
    data: list[WalletResponse]
