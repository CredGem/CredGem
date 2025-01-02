from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


class DBModel(Base):
    __abstract__ = True

    id: Mapped[str] = mapped_column(String, primary_key=True)  # type hint for id
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DBModelResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class PaginationRequest(BaseModel):
    page: int
    page_size: int


class PaginatedResponse(BaseModel):
    page: int
    page_size: int
    total_count: int
    data: list[Any]

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )
