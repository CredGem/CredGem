from typing import List
from datetime import datetime
from dataclasses import asdict, dataclass
from credgem.api.base import BaseAPI


@dataclass
class CreditTypeBase:
    name: str
    description: str


@dataclass
class CreateCreditTypeRequest(CreditTypeBase):
    pass


@dataclass
class CreditTypeResponse(CreditTypeBase):
    id: str
    created_at: datetime
    updated_at: datetime


class UpdateCreditTypeRequest(CreditTypeBase):
    pass


@dataclass
class PaginatedCreditTypeResponse:
    page: int
    page_size: int
    total_count: int
    data: List[CreditTypeResponse]


class CreditTypesAPI(BaseAPI):
    async def create(self, name: str, description: str) -> CreditTypeResponse:
        """Create a new credit type"""
        data = asdict(CreateCreditTypeRequest(name=name, description=description))
        return await self._post(
            "/credit-types", json=data, response_model=CreditTypeResponse
        )

    async def get(self, credit_type_id: str) -> CreditTypeResponse:
        """Get a credit type by ID"""
        return await self._get(
            f"/credit-types/{credit_type_id}", response_model=CreditTypeResponse
        )

    async def update(
        self, credit_type_id: str, name: str, description: str
    ) -> CreditTypeResponse:
        """Update a credit type"""
        data = asdict(UpdateCreditTypeRequest(name=name, description=description))
        return await self._put(
            f"/credit-types/{credit_type_id}",
            json=data,
            response_model=CreditTypeResponse,
        )

    async def list(
        self, page: int = 1, page_size: int = 50
    ) -> PaginatedCreditTypeResponse:
        """List all credit types"""
        params = {"page": page, "page_size": page_size}
        return await self._get(
            "/credit-types", params=params, response_model=PaginatedCreditTypeResponse
        )
