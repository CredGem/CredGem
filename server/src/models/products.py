from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import DBModel, DBModelResponse, PaginatedResponse
from src.models.credit_types import CreditType
from src.models.wallets import Wallet


class SubscriptionType(str, Enum):
    ONE_TIME = "ONE_TIME"
    RECURRING = "RECURRING"


class SubscriptionMode(str, Enum):
    ADD = "ADD"
    RESET = "RESET"


class ProductStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class SubscriptionStatus(str, Enum):
    PENDING = "PENDING"  # Subscription created but not yet started
    ACTIVE = "ACTIVE"  # Currently active subscription
    COMPLETED = "COMPLETED"  # Successfully finished/expired
    CANCELLED = "CANCELLED"  # Terminated before completion
    FAILED = "FAILED"  # Failed to process/apply


# Pydantic models for API responses
class ProductSettingsResponse(DBModelResponse):
    product_id: str
    credit_type_id: str
    credit_amount: float


class ProductResponse(DBModelResponse):
    name: str
    description: str
    status: ProductStatus
    settings: List[ProductSettingsResponse]


class ProductSubscriptionResponse(DBModelResponse):
    product_id: str
    wallet_id: str
    status: SubscriptionStatus
    settings_snapshot: List[Dict]


class Product(DBModel):
    """Base product template that defines credit offerings"""

    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("name", name="uq_product_name"),)

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[ProductStatus] = mapped_column(
        SQLAlchemyEnum(ProductStatus), nullable=False, default=ProductStatus.ACTIVE
    )

    # Relationships
    settings: Mapped[List["ProductSettings"]] = relationship(
        "ProductSettings",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    subscriptions: Mapped[List["ProductSubscription"]] = relationship(
        "ProductSubscription",
        back_populates="product",
        lazy="raise",
    )

    def to_response(self) -> ProductResponse:
        return ProductResponse(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            name=self.name,
            description=self.description,
            status=self.status,
            settings=[setting.to_response() for setting in self.settings],
        )


class PydanticProductSettings(BaseModel):
    id: str
    product_id: str
    credit_type_id: str
    credit_amount: float


class ProductSettings(DBModel):
    """Credit settings for a product"""

    __tablename__ = "product_credit_settings"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "credit_type_id",
            name="uq_product_credit_type",
        ),
    )

    product_id: Mapped[str] = mapped_column(
        String, ForeignKey("products.id"), nullable=False
    )
    credit_type_id: Mapped[str] = mapped_column(
        String, ForeignKey("credit_types.id"), nullable=False
    )
    credit_amount: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    product: Mapped[Product] = relationship("Product", back_populates="settings")
    credit_type: Mapped[CreditType] = relationship("CreditType")

    def to_response(self) -> ProductSettingsResponse:
        return ProductSettingsResponse(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            product_id=self.product_id,
            credit_type_id=self.credit_type_id,
            credit_amount=self.credit_amount,
        )


class ProductSubscription(DBModel):
    """Record of how products are applied to wallets"""

    __tablename__ = "product_subscriptions"

    product_id: Mapped[str] = mapped_column(
        String, ForeignKey("products.id"), nullable=False
    )
    wallet_id: Mapped[str] = mapped_column(
        String, ForeignKey("wallets.id"), nullable=False
    )
    settings_snapshot: Mapped[List[dict]] = mapped_column(JSONB, nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLAlchemyEnum(SubscriptionStatus),
        nullable=False,
        default=SubscriptionStatus.ACTIVE,
    )
    type: Mapped[SubscriptionType] = mapped_column(
        SQLAlchemyEnum(SubscriptionType),
        nullable=False,
        default=SubscriptionType.ONE_TIME,
    )
    mode: Mapped[SubscriptionMode] = mapped_column(
        SQLAlchemyEnum(SubscriptionMode),
        nullable=False,
        default=SubscriptionMode.ADD,
    )

    # Relationships
    product: Mapped[Product] = relationship("Product", back_populates="subscriptions")
    wallet: Mapped[Wallet] = relationship("Wallet")

    def to_response(self) -> ProductSubscriptionResponse:
        return ProductSubscriptionResponse(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            product_id=self.product_id,
            wallet_id=self.wallet_id,
            status=self.status,
            settings_snapshot=self.settings_snapshot,
        )


class ProductSubscriptionRequest(BaseModel):
    product_id: str
    type: SubscriptionType
    mode: SubscriptionMode


# Request models
class CreditSettingsRequest(BaseModel):
    credit_type_id: str
    credit_amount: float


class CreateProductRequest(BaseModel):
    name: str
    description: str
    settings: List[CreditSettingsRequest]


class UpdateProductRequest(BaseModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)


class PaginatedProductResponse(PaginatedResponse):
    data: List[ProductResponse]
