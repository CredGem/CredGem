from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from src.core.settings import settings

pytestmark = pytest.mark.anyio


async def test_create_credit_type(client: AsyncClient):
    response = await client.post(
        f"{settings.API_V1_STR}/credit-types",
        json={"name": "Test Credit Type", "description": "Test Description"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "Test Credit Type"
    assert response.json()["description"] == "Test Description"


async def test_get_credit_types(client: AsyncClient):
    # Create test credit types
    for i in range(3):
        response = await client.post(
            f"{settings.API_V1_STR}/credit-types",
            json={
                "name": f"Test Credit Type {i}",
                "description": f"Test Description {i}",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    # Get all credit types
    response = await client.get(f"{settings.API_V1_STR}/credit-types")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) >= 3


async def test_update_credit_type(client: AsyncClient):
    # Create a credit type
    response = await client.post(
        f"{settings.API_V1_STR}/credit-types",
        json={"name": "Test Credit Type", "description": "Test Description"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    credit_type_id = response.json()["id"]

    # Update the credit type
    response = await client.put(
        f"{settings.API_V1_STR}/credit-types/{credit_type_id}",
        json={"name": "Updated Credit Type", "description": "Updated Description"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Updated Credit Type"
    assert response.json()["description"] == "Updated Description"


async def test_delete_credit_type(client: AsyncClient):
    # Create a credit type
    response = await client.post(
        f"{settings.API_V1_STR}/credit-types",
        json={"name": "Test Credit Type", "description": "Test Description"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    credit_type_id = response.json()["id"]

    # Delete the credit type
    response = await client.delete(
        f"{settings.API_V1_STR}/credit-types/{credit_type_id}"
    )
    assert response.status_code == status.HTTP_200_OK

    # Verify deletion
    response = await client.get(f"{settings.API_V1_STR}/credit-types")
    assert response.status_code == status.HTTP_200_OK
    credit_types = response.json()
    assert not any(ct["id"] == credit_type_id for ct in credit_types)


async def test_update_nonexistent_credit_type(client: AsyncClient):
    nonexistent_id = str(uuid4())
    response = await client.put(
        f"{settings.API_V1_STR}/credit-types/{nonexistent_id}",
        json={"name": "Updated Credit Type", "description": "Updated Description"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_nonexistent_credit_type(client: AsyncClient):
    nonexistent_id = str(uuid4())
    response = await client.delete(
        f"{settings.API_V1_STR}/credit-types/{nonexistent_id}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
