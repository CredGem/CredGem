from typing import Any, Dict, List, Optional

from credgem.models.transactions import TransactionResponse

from .base import BaseAPI


class TransactionsAPI(BaseAPI):
    """API client for transaction operations."""

    async def hold(
        self,
        wallet_id: str,
        credit_type_id: str,
        amount: float,
        description: Optional[str] = None,
        issuer: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        external_transaction_id: Optional[str] = None,
    ) -> TransactionResponse:
        payload = {
            "type": "hold",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "context": context or {},
            "payload": {"type": "hold", "amount": amount},
        }
        if external_transaction_id:
            payload["external_transaction_id"] = external_transaction_id

        response = await self._post(
            f"/wallets/{wallet_id}/hold", json=payload, response_model=None
        )
        return TransactionResponse.from_dict(response)

    async def debit(
        self,
        wallet_id: str,
        credit_type_id: str,
        amount: float,
        description: Optional[str] = None,
        issuer: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        hold_transaction_id: Optional[str] = None,
        external_transaction_id: Optional[str] = None,
    ) -> TransactionResponse:
        payload = {
            "type": "debit",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "context": context or {},
            "payload": {
                "type": "debit",
                "amount": str(amount),
                "hold_external_transaction_id": hold_transaction_id
                if hold_transaction_id
                else None,
            },
        }
        if external_transaction_id:
            payload["external_transaction_id"] = external_transaction_id

        try:
            response = await self._post(
                f"/wallets/{wallet_id}/debit", json=payload, response_model=None
            )
            debit_response = TransactionResponse.from_dict(response)

            # If this was a debit with hold, release the hold
            if hold_transaction_id:
                await self.release(
                    wallet_id=wallet_id,
                    hold_transaction_id=hold_transaction_id,
                    credit_type_id=credit_type_id,
                    description=description,
                    issuer=issuer,
                    context=context,
                    external_transaction_id=f"release_{external_transaction_id}"
                    if external_transaction_id
                    else None,
                )

            return debit_response
        except Exception as e:
            if hold_transaction_id and "invalid hold" in str(e).lower():
                raise ValueError("Invalid hold transaction ID") from e
            raise

    async def release(
        self,
        wallet_id: str,
        hold_transaction_id: str,
        credit_type_id: str,
        description: str,
        issuer: str,
        context: Optional[Dict[str, Any]] = None,
        external_transaction_id: Optional[str] = None,
    ) -> TransactionResponse:
        """Release a hold on credits in a wallet."""
        payload = {
            "type": "release",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "context": context or {},
            "payload": {"type": "release", "hold_transaction_id": hold_transaction_id},
        }

        if external_transaction_id is not None:
            payload["external_transaction_id"] = external_transaction_id

        response = await self._post(
            f"/wallets/{wallet_id}/release",
            json=payload,
        )

        return TransactionResponse.from_dict(response)

    async def deposit(
        self,
        wallet_id: str,
        credit_type_id: str,
        amount: float,
        description: Optional[str] = None,
        issuer: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> TransactionResponse:
        payload = {
            "type": "deposit",
            "credit_type_id": credit_type_id,
            "description": description,
            "issuer": issuer,
            "context": context or {},
            "payload": {"type": "deposit", "amount": str(amount)},
        }

        response = await self._post(
            f"/wallets/{wallet_id}/deposit", json=payload, response_model=None
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
        external_transaction_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> List[TransactionResponse]:
        """List transactions with optional filtering."""
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if wallet_id:
            params["wallet_id"] = wallet_id
        if external_transaction_id:
            params["external_transaction_id"] = external_transaction_id
        response = await self._get("/transactions", params=params)
        return [
            TransactionResponse.from_dict(item) for item in response.get("data", [])
        ]
