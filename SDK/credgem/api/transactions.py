from typing import Any, Dict, List, Optional

from credgem.models.transactions import (
    DebitRequest,
    DepositRequest,
    HoldRequest,
    ReleaseRequest,
    TransactionResponse,
)

from .base import BaseAPI


class TransactionsAPI(BaseAPI):
    """API client for transaction operations."""

    async def hold(
        self,
        request: HoldRequest,
    ) -> TransactionResponse:
        payload = {
            "type": "hold",
            "credit_type_id": request.credit_type_id,
            "description": request.description,
            "issuer": request.issuer,
            "context": request.context or {},
            "payload": {"type": "hold", "amount": request.amount},
        }
        if request.external_id:
            payload["external_id"] = request.external_id

        response = await self._post(
            f"/wallets/{request.wallet_id}/hold", json=payload, response_model=None
        )
        return TransactionResponse.from_dict(response)

    async def debit(
        self,
        request: DebitRequest,
    ) -> TransactionResponse:
        payload = {
            "type": "debit",
            "credit_type_id": request.credit_type_id,
            "description": request.description,
            "issuer": request.issuer,
            "context": request.context or {},
            "payload": {
                "type": "debit",
                "amount": str(request.amount),
                "hold_transaction_id": request.hold_transaction_id
                if request.hold_transaction_id
                else None,
            },
        }
        if request.external_id:
            payload["external_id"] = request.external_id

        try:
            response = await self._post(
                f"/wallets/{request.wallet_id}/debit", json=payload, response_model=None
            )
            return TransactionResponse.from_dict(response)

        except Exception as e:
            if request.hold_transaction_id and "invalid hold" in str(e).lower():
                raise ValueError("Invalid hold transaction ID") from e
            raise

    async def release(
        self,
        request: ReleaseRequest,
    ) -> TransactionResponse:
        """Release a hold on credits in a wallet."""
        payload = {
            "type": "release",
            "credit_type_id": request.credit_type_id,
            "description": request.description,
            "issuer": request.issuer,
            "context": request.context or {},
            "payload": {
                "type": "release",
                "hold_transaction_id": request.hold_transaction_id,
            },
        }

        if request.external_id is not None:
            payload["external_id"] = request.external_id

        response = await self._post(
            f"/wallets/{request.wallet_id}/release",
            json=payload,
        )

        return TransactionResponse.from_dict(response)

    async def deposit(
        self,
        request: DepositRequest,
    ) -> TransactionResponse:
        payload = {
            "type": "deposit",
            "credit_type_id": request.credit_type_id,
            "description": request.description,
            "issuer": request.issuer,
            "context": request.context or {},
            "payload": {"type": "deposit", "amount": str(request.amount)},
        }

        response = await self._post(
            f"/wallets/{request.wallet_id}/deposit", json=payload, response_model=None
        )
        return TransactionResponse.from_dict(response)

    async def get(self, transaction_id: str) -> TransactionResponse:
        response = await self._get(
            f"/transactions/{transaction_id}", response_model=None
        )
        return TransactionResponse.from_dict(response)

    async def list(
        self,
        wallet_id: Optional[str] = None,
        external_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> List[TransactionResponse]:
        """List transactions with optional filtering."""
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if wallet_id:
            params["wallet_id"] = wallet_id
        if external_id:
            params["external_id"] = external_id
        response = await self._get("/transactions", params=params)
        return [
            TransactionResponse.from_dict(item) for item in response.get("data", [])
        ]
