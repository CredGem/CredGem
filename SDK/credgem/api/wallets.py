from typing import Any, Dict, Optional

from credgem.models.wallets import (
    PaginatedWalletResponse,
    WalletRequest,
    WalletResponse,
    WalletUpdateRequest,
)

from ..utils import get_context_filter
from .base import BaseAPI


class WalletsAPI(BaseAPI):
    async def create(
        self,
        request: WalletRequest,
    ) -> WalletResponse:
        payload: Dict[str, Any] = {
            "name": request.name,
        }
        if request.description is not None:
            payload["description"] = request.description
        if request.context:
            payload["context"] = request.context

        response = await self._post("/wallets", json=payload, response_model=None)
        # Ensure description is properly set in the response
        if request.description is not None and "description" not in response:
            response["description"] = request.description
        return WalletResponse.from_dict(response)

    async def get(self, wallet_id: str) -> WalletResponse:
        response = await self._get(f"/wallets/{wallet_id}", response_model=None)
        return WalletResponse.from_dict(response)

    async def list(
        self,
        page: int = 1,
        page_size: int = 50,
        context: Optional[Dict[str, Any]] = None,
    ) -> PaginatedWalletResponse:
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if context is not None:
            params["context"] = get_context_filter(context)
        response = await self._get("/wallets", params=params, response_model=None)
        return PaginatedWalletResponse(
            data=[
                WalletResponse.from_dict(wallet) for wallet in response.get("data", [])
            ],
            page=response.get("page", page),
            page_size=response.get("page_size", page_size),
            total_count=response.get("total_count", 0),
        )

    async def update(
        self,
        wallet_id: str,
        request: WalletUpdateRequest,
    ) -> WalletResponse:
        payload = {}
        if request.name is not None:
            payload["name"] = request.name
        if request.description is not None:
            payload["description"] = request.description
        if request.context is not None:
            payload["context"] = request.context

        response = await self._put(
            f"/wallets/{wallet_id}", json=payload, response_model=None
        )
        return WalletResponse.from_dict(response)

    async def delete(self, wallet_id: str) -> None:
        await self._delete(f"/wallets/{wallet_id}", response_model=None)
