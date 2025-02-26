from uuid import uuid4

import httpx
import pytest

from src.core.settings import settings
from src.models.wallets import CreateWalletRequest, UpdateWalletRequest

pytestmark = pytest.mark.anyio


class TestWalletEndpoints:
    base_url = f"{settings.API_V1_STR}"

    async def test_create_wallet(self, client: httpx.AsyncClient):
        user_id = str(uuid4())
        wallet_name = f"test_wallet_{user_id}"
        # Test creating a new wallet
        request = CreateWalletRequest(name=wallet_name, context={"user_id": user_id})
        response = await client.post(
            f"{self.base_url}/wallets/", json=request.model_dump()
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == wallet_name
        assert data["context"]["user_id"] == user_id
        assert "id" in data

    async def test_create_wallet_with_same_external_id(
        self, client: httpx.AsyncClient
    ):
        user_id = str(uuid4())
        wallet_name = f"test_wallet_{user_id}"
        external_id = str(uuid4())
        request = CreateWalletRequest(
            name=wallet_name,
            context={"user_id": user_id},
            external_id=external_id,
        )
        response = await client.post(
            f"{self.base_url}/wallets/", json=request.model_dump()
        )
        assert response.status_code == 201

        # Test creating a new wallet with the same external transaction ID
        request = CreateWalletRequest(
            name=wallet_name,
            context={"user_id": user_id},
            external_id=external_id,
        )
        response = await client.post(
            f"{self.base_url}/wallets/", json=request.model_dump()
        )
        assert response.status_code == 409

    async def test_update_wallet(self, client: httpx.AsyncClient):
        user_id = str(uuid4())
        wallet_name = f"test_wallet_{user_id}"
        request = CreateWalletRequest(name=wallet_name, context={"user_id": user_id})
        response = await client.post(
            f"{self.base_url}/wallets/", json=request.model_dump()
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == wallet_name
        assert data["context"]["user_id"] == user_id

        wallet_id = data["id"]
        update_request = UpdateWalletRequest(name=f"updated_{wallet_name}")
        response = await client.put(
            f"{self.base_url}/wallets/{wallet_id}", json=update_request.model_dump()
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == f"updated_{wallet_name}"
        assert data["context"]["user_id"] == user_id

    async def test_get_wallet(self, client: httpx.AsyncClient):
        # Create a wallet first
        user_id = str(uuid4())
        wallet_name = f"test_wallet_{user_id}"
        create_request = CreateWalletRequest(
            name=wallet_name, context={"user_id": user_id}
        )
        create_response = await client.post(
            f"{self.base_url}/wallets/", json=create_request.model_dump()
        )
        wallet_id = create_response.json()["id"]

        # Test getting the wallet
        response = await client.get(f"{self.base_url}/wallets/{wallet_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == wallet_name
        assert data["context"]["user_id"] == user_id
        assert "balances" in data

    async def test_get_nonexistent_wallet(self, client: httpx.AsyncClient):
        nonexistent_id = str(uuid4())
        response = await client.get(f"{self.base_url}/wallets/{nonexistent_id}")
        assert response.status_code == 404

    async def test_list_wallets_with_multiple_wallets(self, client: httpx.AsyncClient):
        # Create first wallet
        user_id = str(uuid4())
        wallet_name_1 = f"test_wallet_1_{user_id}"

        create_request_1 = CreateWalletRequest(
            name=wallet_name_1, context={"user_id": user_id}
        )

        create_response_1 = await client.post(
            f"{self.base_url}/wallets/", json=create_request_1.model_dump()
        )
        assert create_response_1.status_code == 201
        wallet_id_1 = create_response_1.json()["id"]

        # Create second wallet
        wallet_name_2 = f"test_wallet_2_{user_id}"

        create_request_2 = CreateWalletRequest(
            name=wallet_name_2, context={"user_id": user_id}
        )

        create_response_2 = await client.post(
            f"{self.base_url}/wallets/", json=create_request_2.model_dump()
        )
        assert create_response_2.status_code == 201

        query_params = {
            "page": 1,
            "page_size": 10,
            "context": f"[user_id={user_id}]",
            "name": wallet_name_1,
        }
        response = await client.get(f"{self.base_url}/wallets/", params=query_params)
        assert response.status_code == 200
        response = response.json()
        assert response["data"][0]["id"] == wallet_id_1

    async def test_list_wallets_empty_result(self, client: httpx.AsyncClient):
        user_id = str(uuid4())
        query_params = {
            "page": 1,
            "page_size": 10,
            "context": f"[user_id={user_id}]",
        }
        response = await client.get(f"{self.base_url}/wallets/", params=query_params)
        assert response.status_code == 200
        response = response.json()
        assert len(response["data"]) == 0

    async def test_list_wallets_pagination(self, client: httpx.AsyncClient):
        user_id = str(uuid4())
        # Create 15 wallets
        for i in range(15):
            wallet_name = f"test_wallet_{i}_{user_id}"
            create_request = CreateWalletRequest(
                name=wallet_name, context={"user_id": user_id}
            )
            await client.post(
                f"{self.base_url}/wallets/", json=create_request.model_dump()
            )

        # Test first page
        query_params = {
            "page": 1,
            "page_size": 10,
            "context": f"[user_id={user_id}]",
        }
        response = await client.get(f"{self.base_url}/wallets/", params=query_params)
        assert response.status_code == 200
        response = response.json()
        assert len(response["data"]) == 10

        # Test second page
        query_params = {
            "page": 2,
            "page_size": 10,
            "context": f"[user_id={user_id}]",
        }

        response = await client.get(f"{self.base_url}/wallets/", params=query_params)
        assert response.status_code == 200
        response = response.json()
        assert len(response["data"]) == 5

    async def test_list_wallets_by_context(self, client: httpx.AsyncClient):
        # Create wallets with different contexts
        user_id_1 = str(uuid4())
        user_id_2 = str(uuid4())
        tenant_1 = "tenant_1"
        tenant_2 = "tenant_2"

        # Create wallet with user_id_1 and tenant_1
        create_request_1 = CreateWalletRequest(
            name="wallet_1", context={"user_id": user_id_1, "tenant": tenant_1}
        )
        await client.post(
            f"{self.base_url}/wallets/", json=create_request_1.model_dump()
        )

        # Create wallet with user_id_1 and tenant_2
        create_request_2 = CreateWalletRequest(
            name="wallet_2", context={"user_id": user_id_1, "tenant": tenant_2}
        )
        await client.post(
            f"{self.base_url}/wallets/", json=create_request_2.model_dump()
        )

        # Create wallet with user_id_2 and tenant_1
        create_request_3 = CreateWalletRequest(
            name="wallet_3", context={"user_id": user_id_2, "tenant": tenant_1}
        )
        await client.post(
            f"{self.base_url}/wallets/", json=create_request_3.model_dump()
        )

        # Test filtering by single context parameter
        query_params = {"context": f"[user_id={user_id_1}]"}
        response = await client.get(f"{self.base_url}/wallets/", params=query_params)
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["data"]) == 2

        # Test filtering by multiple context parameters
        query_params = {"context": f"[user_id={user_id_1},tenant={tenant_1}]"}
        response = await client.get(f"{self.base_url}/wallets/", params=query_params)
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["data"]) == 1
        assert response_data["data"][0]["name"] == "wallet_1"

    async def test_list_wallets_by_name(self, client: httpx.AsyncClient):
        # Create wallets with different names
        unique_id = str(uuid4())
        user_id = str(uuid4())
        user_id_2 = str(uuid4())
        wallet_name_1 = f"wallet_1_{unique_id}"
        wallet_name_2 = f"wallet_2_{unique_id}"

        # Create wallets
        create_request_1 = CreateWalletRequest(
            name=wallet_name_1, context={"user_id": user_id}
        )
        create_request_2 = CreateWalletRequest(
            name=wallet_name_2, context={"user_id": user_id}
        )
        create_request_3 = CreateWalletRequest(
            name=wallet_name_1, context={"user_id": user_id_2}
        )

        await client.post(
            f"{self.base_url}/wallets/", json=create_request_1.model_dump()
        )
        await client.post(
            f"{self.base_url}/wallets/", json=create_request_2.model_dump()
        )
        await client.post(
            f"{self.base_url}/wallets/", json=create_request_3.model_dump()
        )

        # Test filtering by name
        query_params = {"name": wallet_name_1}
        response = await client.get(f"{self.base_url}/wallets/", params=query_params)
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["data"]) == 2
        assert response_data["data"][0]["name"] == wallet_name_1
