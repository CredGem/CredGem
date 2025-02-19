from typing import List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

from credgem.api.base import BaseAPI


class WalletStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class BalanceResponse:
    id: str
    created_at: datetime
    updated_at: datetime
    wallet_id: str
    credit_type_id: str
    available: float
    held: float
    spent: float
    overall_spent: float


@dataclass
class WalletBase:
    name: str
    context: dict


@dataclass
class CreateWalletRequest(WalletBase):
    pass


@dataclass
class WalletResponse(WalletBase):
    id: str
    balances: List[BalanceResponse]
    status: WalletStatus
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        self.balances = [BalanceResponse(**balance) for balance in self.balances]


@dataclass
class UpdateWalletRequest:
    name: Optional[str] = None
    context: Optional[dict] = None


@dataclass
class PaginatedWalletResponse:
    page: int
    page_size: int
    total_count: int
    data: List[WalletResponse]


class WalletsAPI(BaseAPI):
    async def create(self, name: str, context: dict = {}) -> WalletResponse:
        """Create a new wallet"""
        data = asdict(CreateWalletRequest(name=name, context=context))
        return await self._post("/wallets", json=data, response_model=WalletResponse)

    async def get(self, wallet_id: str) -> WalletResponse:
        """Get a wallet by ID"""
        return await self._get(f"/wallets/{wallet_id}", response_model=WalletResponse)

    async def update(
        self, wallet_id: str, name: str | None = None, context: dict | None = None
    ) -> WalletResponse:
        """Update a wallet"""
        data = {}
        if name is not None:
            data["name"] = name
        if context is not None:
            data["context"] = context
        return await self._put(
            f"/wallets/{wallet_id}", json=data, response_model=WalletResponse
        )

    async def list(self, page: int = 1, page_size: int = 50) -> PaginatedWalletResponse:
        """List all wallets"""
        params = {"page": page, "page_size": page_size}
        return await self._get(
            "/wallets", params=params, response_model=PaginatedWalletResponse
        )
