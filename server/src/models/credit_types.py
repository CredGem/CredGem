from pydantic import BaseModel
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import DBModel, DBModelResponse


class CreditTypeResponse(DBModelResponse):
    name: str
    description: str


class CreditType(DBModel):
    __tablename__ = "credit_types"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)

    def to_response(self) -> CreditTypeResponse:
        return CreditTypeResponse(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            name=self.name,
            description=self.description,
        )


class CreateCreditTypeRequest(BaseModel):
    name: str
    description: str


class UpdateCreditTypeRequest(BaseModel):
    name: str
    description: str
