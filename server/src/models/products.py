from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import DBModel, DBModelResponse, PaginatedResponse
from src.models.credit_types import CreditType
from src.models.wallets import Wallet


class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ApplicationStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ApplicationHistoryStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ApplicationType(str, Enum):
    ONE_TIME = "one_time"
    RECURRING = "recurring"


class ApplicationMode(str, Enum):
    ADD = "add"
    RESET = "reset"


class Product(DBModel):
    """Base product template that defines credit offerings"""

    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("name", name="uq_product_name"),)

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[ProductStatus] = mapped_column(
        SQLAlchemyEnum(ProductStatus), nullable=False, default=ProductStatus.ACTIVE
    )
    active_version_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    versions: Mapped[List["ProductVersion"]] = relationship(
        "ProductVersion",
        back_populates="product",
        order_by="desc(ProductVersion.created_at)",
        foreign_keys=[active_version_id],
    )
    active_version: Mapped[Optional["ProductVersion"]] = relationship(
        "ProductVersion",
        back_populates="product",
        primaryjoin="and_(Product.active_version_id==ProductVersion.id, "
        "Product.id==ProductVersion.product_id)",
        uselist=False,
    )


class ProductVersion(DBModel):
    """Version of a product with global settings"""

    __tablename__ = "product_versions"
    __table_args__ = (
        UniqueConstraint("product_id", "version", name="uq_product_version"),
    )

    product_id: Mapped[str] = mapped_column(
        String, ForeignKey("products.id"), nullable=False
    )
    version: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    product: Mapped[Product] = relationship(
        "Product",
        back_populates="versions",
        foreign_keys=[product_id],
    )
    credit_settings: Mapped[List["ProductVersionCreditSettings"]] = relationship(
        "ProductVersionCreditSettings",
        back_populates="version",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class ProductVersionCreditSettings(DBModel):
    """Credit type specific settings for a product version"""

    __tablename__ = "product_version_credit_settings"
    __table_args__ = (
        UniqueConstraint(
            "product_version_id",
            "credit_type_id",
            name="uq_product_version_credit_type",
        ),
    )
    product_id: Mapped[str] = mapped_column(
        String, ForeignKey("products.id"), nullable=False
    )
    product_version_id: Mapped[str] = mapped_column(
        String, ForeignKey("product_versions.id"), nullable=False
    )
    credit_type_id: Mapped[str] = mapped_column(
        String, ForeignKey("credit_types.id"), nullable=False
    )
    # Credit settings
    credit_amount: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    credit_type: Mapped[CreditType] = relationship(
        "CreditType", lazy="raise", foreign_keys=[credit_type_id]
    )
    version: Mapped[ProductVersion] = relationship(
        "ProductVersion", lazy="raise", foreign_keys=[product_version_id]
    )
    product: Mapped[Product] = relationship(
        "Product", lazy="raise", foreign_keys=[product_id]
    )


class ProductApplication(DBModel):
    """Record of how products are applied to wallets"""

    __tablename__ = "product_applications"

    product_id: Mapped[str] = mapped_column(
        String, ForeignKey("products.id"), nullable=False
    )
    product_version_id: Mapped[str] = mapped_column(
        String, ForeignKey("product_versions.id"), nullable=False
    )
    application_type: Mapped[ApplicationType] = mapped_column(
        SQLAlchemyEnum(ApplicationType),
        nullable=False,
        default=ApplicationType.ONE_TIME,
    )
    application_mode: Mapped[ApplicationMode] = mapped_column(
        SQLAlchemyEnum(ApplicationMode), nullable=False, default=ApplicationMode.ADD
    )
    wallet_id: Mapped[str] = mapped_column(
        String, ForeignKey("wallets.id"), nullable=False
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        SQLAlchemyEnum(ApplicationStatus),
        nullable=False,
        default=ApplicationStatus.ACTIVE,
    )
    context: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})

    product: Mapped[Product] = relationship(
        "Product", back_populates="applications", foreign_keys=[product_id]
    )
    product_version: Mapped[ProductVersion] = relationship(
        "ProductVersion",
        back_populates="applications",
        foreign_keys=[product_version_id],
    )
    wallet: Mapped[Wallet] = relationship("Wallet", foreign_keys=[wallet_id])
    history: Mapped[List["ApplicationHistory"]] = relationship(
        "ApplicationHistory",
        back_populates="application",
        order_by="desc(ApplicationHistory.created_at)",
    )

    def to_response(self) -> "ProductApplicationResponse":
        return ProductApplicationResponse(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            product_id=self.product_id,
            product_version_id=self.product_version_id,
            wallet_id=self.wallet_id,
            status=self.status,
            metadata=self.context,
            expires_at=self.expires_at,
            history=[h.to_response() for h in self.history],
        )


class ApplicationHistory(DBModel):
    """History of events for product applications"""

    __tablename__ = "application_history"

    application_id: Mapped[str] = mapped_column(
        String, ForeignKey("product_applications.id"), nullable=False
    )
    status: Mapped[ApplicationHistoryStatus] = mapped_column(
        SQLAlchemyEnum(ApplicationHistoryStatus), nullable=False
    )
    details: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})

    application: Mapped[ProductApplication] = relationship(
        "ProductApplication",
        back_populates="history",
        foreign_keys=[application_id],
    )

    def to_response(self) -> "ApplicationHistoryResponse":
        return ApplicationHistoryResponse(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            application_id=self.application_id,
            status=self.status,
            details=self.details,
        )


# Pydantic response models
class ProductResponse(DBModelResponse):
    name: str
    description: str
    status: ProductStatus
    context: Dict
    versions: List["ProductVersionResponse"]


class ProductVersionResponse(DBModelResponse):
    product_id: str
    version: str
    credit_type_id: str
    credit_amount: float
    validity_days: Optional[int]
    settings: Dict


class ProductApplicationResponse(DBModelResponse):
    product_id: str
    product_version_id: str
    wallet_id: str
    status: ApplicationStatus
    metadata: Dict
    expires_at: Optional[datetime]
    history: List["ApplicationHistoryResponse"]


class ApplicationHistoryResponse(DBModelResponse):
    application_id: str
    status: ApplicationHistoryStatus
    details: Dict


# Request models
class CreateProductRequest(BaseModel):
    name: str
    description: str
    metadata: Dict = {}


class CreateProductVersionRequest(BaseModel):
    version: str
    credit_type_id: str
    credit_amount: float
    validity_days: Optional[int] = None
    settings: Dict = {}


class CreateProductApplicationRequest(BaseModel):
    product_id: str
    product_version_id: str
    wallet_id: str
    metadata: Dict = {}


# Paginated response models
class PaginatedProductResponse(PaginatedResponse):
    data: List[ProductResponse]


class PaginatedProductApplicationResponse(PaginatedResponse):
    data: List[ProductApplicationResponse]
