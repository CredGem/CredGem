from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from credgem.api.base import BaseAPI


class WalletStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class BalanceResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    wallet_id: str
    credit_type_id: str
    available: float
    held: float
    spent: float
    overall_spent: float


class WalletBase(BaseModel):
    name: str
    description: Optional[str] = None
    context: dict = {}


class CreateWalletRequest(WalletBase):
    pass


class WalletResponse(WalletBase):
    id: str
    balances: List[BalanceResponse]
    status: WalletStatus
    created_at: datetime
    updated_at: datetime


class UpdateWalletRequest(BaseModel):
    name: Optional[str] = None
    context: Optional[dict] = None


class PaginatedWalletResponse(BaseModel):
    page: int
    page_size: int
    total_count: int
    data: List[WalletResponse]


class WalletsAPI(BaseAPI):
    async def create(self, name: str, description: Optional[str] = None, context: dict = {}) -> WalletResponse:
        """Create a new wallet"""
        data = CreateWalletRequest(name=name, description=description, context=context).model_dump()
        return await self._post("/wallets", json=data, response_model=WalletResponse)

    async def get(self, wallet_id: str) -> WalletResponse:
        """Get a wallet by ID"""
        return await self._get(f"/wallets/{wallet_id}", response_model=WalletResponse)

    async def update(
        self, wallet_id: str, name: Optional[str] = None, context: Optional[dict] = None
    ) -> WalletResponse:
        """Update a wallet"""
        data = UpdateWalletRequest(name=name, context=context).model_dump(exclude_none=True)
        return await self._put(f"/wallets/{wallet_id}", json=data, response_model=WalletResponse)

    async def list(
        self, page: int = 1, page_size: int = 50
    ) -> PaginatedWalletResponse:
        """List all wallets"""
        params = {"page": page, "page_size": page_size}
        return await self._get("/wallets", params=params, response_model=PaginatedWalletResponse) 