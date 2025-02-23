from typing import List, Optional

from ..models.credit_types import (
    CreditTypeRequest,
    CreditTypeResponse,
    CreditTypeUpdateRequest,
)
from .base import BaseAPI


class CreditTypesAPI(BaseAPI):
    async def create(
        self,
        request: CreditTypeRequest,
    ) -> CreditTypeResponse:
        payload = {"name": request.name}
        if request.description is not None:
            payload["description"] = request.description

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
        request: CreditTypeUpdateRequest,
    ) -> CreditTypeResponse:
        payload = {}
        if request.name is not None:
            payload["name"] = request.name
        if request.description is not None:
            payload["description"] = request.description

        response = await self._put(
            f"/credit-types/{credit_type_id}", json=payload, response_model=None
        )
        return CreditTypeResponse.from_dict(response)

    async def delete(self, credit_type_id: str) -> None:
        await self._delete(f"/credit-types/{credit_type_id}", response_model=None)
