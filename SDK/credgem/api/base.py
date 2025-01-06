from typing import Any, Dict, Optional, Type, TypeVar

from httpx import AsyncClient
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseAPI:
    def __init__(self, client: AsyncClient):
        self._client = client

    async def _get(
        self, path: str, params: Optional[Dict[str, Any]] = None, response_model: Type[T] = None
    ) -> T:
        response = await self._client.get(path, params=params)
        response.raise_for_status()
        data = response.json()
        return response_model.model_validate(data) if response_model else data

    async def _post(
        self, path: str, json: Dict[str, Any], response_model: Type[T] = None
    ) -> T:
        response = await self._client.post(path, json=json)
        response.raise_for_status()
        data = response.json()
        return response_model.model_validate(data) if response_model else data

    async def _put(
        self, path: str, json: Dict[str, Any], response_model: Type[T] = None
    ) -> T:
        response = await self._client.put(path, json=json)
        response.raise_for_status()
        data = response.json()
        return response_model.model_validate(data) if response_model else data

    async def _delete(
        self, path: str, response_model: Type[T] = None
    ) -> T:
        response = await self._client.delete(path)
        response.raise_for_status()
        data = response.json()
        return response_model.model_validate(data) if response_model else data 