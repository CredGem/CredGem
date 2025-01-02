from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import DBModel, DBModelResponse


class BalanceResponse(DBModelResponse):
    wallet_id: str
    credit_type_id: str
    available: float
    held: float
    spent: float
    overall_spent: float


class BalanceDBModel(DBModel):
    __tablename__ = "balances"

    wallet_id: Mapped[str] = mapped_column(String, ForeignKey("wallets.id"), index=True)
    credit_type_id: Mapped[str] = mapped_column(String, index=True)
    available: Mapped[float] = mapped_column(Float, default=0)
    held: Mapped[float] = mapped_column(Float, default=0)
    spent: Mapped[float] = mapped_column(Float, default=0)
    overall_spent: Mapped[float] = mapped_column(Float, default=0)

    wallet = relationship("Wallet", back_populates="_balances")

    def to_response(self) -> BalanceResponse:
        return BalanceResponse(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            wallet_id=self.wallet_id,
            credit_type_id=self.credit_type_id,
            available=self.available,
            held=self.held,
            spent=self.spent,
            overall_spent=self.overall_spent,
        )
