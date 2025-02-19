from typing import Dict, Any, Optional, List

from .base import BaseAPI
from ..models import CreditTypeResponse


class CreditTypesAPI(BaseAPI):
    async def create(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> CreditTypeResponse:
        payload = {"name": name}
        if description is not None:
            payload["description"] = description

        response = await self._post("/credit-types", json=payload, response_model=None)
        return CreditTypeResponse.from_dict(response)

    async def get(self, credit_type_id: str) -> CreditTypeResponse:
        response = await self._get(
            f"/credit-types/{credit_type_id}", response_model=None
        )
        return CreditTypeResponse.from_dict(response)

    async def list(self) -> List[CreditTypeResponse]:
        response = await self._get("/credit-types", response_model=None)
        return [CreditTypeResponse.from_dict(credit_type) for credit_type in response]

    async def update(
        self,
        credit_type_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> CreditTypeResponse:
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        response = await self._put(
            f"/credit-types/{credit_type_id}", json=payload, response_model=None
        )
        return CreditTypeResponse.from_dict(response)

    async def delete(self, credit_type_id: str) -> None:
        await self._delete(f"/credit-types/{credit_type_id}", response_model=None)
