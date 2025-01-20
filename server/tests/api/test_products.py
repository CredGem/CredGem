from typing import Dict
from uuid import uuid4

import httpx
import pytest

from src.core.settings import settings
from src.models.products import ProductStatus

pytestmark = pytest.mark.anyio


class TestProducts:
    base_url = settings.API_V1_STR

    @pytest.fixture(scope="function")
    async def setup_credit_type(self, client: httpx.AsyncClient):
        yield await self.create_credit_type(client)

    @pytest.fixture(scope="function")
    async def setup_product(
        self,
        client: httpx.AsyncClient,
        setup_credit_type: Dict[str, str],
    ):
        yield await self.create_product(client, setup_credit_type["id"])

    async def create_credit_type(self, client: httpx.AsyncClient):
        credit_type_request = {
            "name": "Default Credit Type",
            "description": "Default credit type for product tests",
        }
        response = await client.post(
            f"{self.base_url}/credit-types", json=credit_type_request
        )
        return response.json()

    async def create_product(self, client: httpx.AsyncClient, credit_type_id: str):
        product_data = {
            "name": f"Test Product {uuid4()}",
            "description": "A test product",
            "settings": [{"credit_type_id": credit_type_id, "credit_amount": 100.0}],
        }
        response = await client.post(f"{self.base_url}/products/", json=product_data)
        return response.json()

    def _find_setting_by_credit_type_id(
        self, product: dict, credit_type_id: str
    ) -> dict | None:
        for setting in product.get("settings", []):
            if setting.get("credit_type_id") == credit_type_id:
                return setting
        return None

    async def test_create_product(self, client: httpx.AsyncClient, setup_credit_type):
        credit_amount = 100.0
        setup_product_data = {
            "name": f"Test Product {uuid4()}",
            "description": "A test product",
            "settings": [
                {
                    "credit_type_id": setup_credit_type["id"],
                    "credit_amount": credit_amount,
                }
            ],
        }
        response = await client.post(
            f"{self.base_url}/products/", json=setup_product_data
        )
        assert response.status_code == 201
        product = response.json()
        assert product["name"] == setup_product_data["name"]
        assert product["description"] == setup_product_data["description"]
        assert product["status"] == ProductStatus.ACTIVE
        setting = self._find_setting_by_credit_type_id(
            product=product, credit_type_id=setup_credit_type["id"]
        )
        assert setting is not None
        assert setting["credit_amount"] == credit_amount

    async def test_get_products(self, client: httpx.AsyncClient, setup_product):
        response = await client.get(f"{self.base_url}/products/")
        assert response.status_code == 200
        response = response.json()
        products = response["data"]
        assert len(products) > 0

    async def test_get_product_by_id(self, client: httpx.AsyncClient, setup_product):
        product_id = setup_product["id"]

        response = await client.get(f"{self.base_url}/products/{product_id}")
        assert response.status_code == 200
        product = response.json()
        assert product["id"] == product_id
        assert product["name"] == setup_product["name"]

    async def test_update_product(self, client: httpx.AsyncClient, setup_product):
        product_id = setup_product["id"]

        update_data = {
            "name": f"Updated Product Name {uuid4()}",
            "description": "Updated description",
        }

        response = await client.put(
            f"{self.base_url}/products/{product_id}", json=update_data
        )
        assert response.status_code == 200
        product = response.json()
        assert product["name"] == update_data["name"]
        assert product["description"] == update_data["description"]

    async def test_create_product_invalid_data(self, client: httpx.AsyncClient):
        invalid_data = {
            "name": "",  # Empty name should be invalid
            "description": "Test description",
            "settings": [],  # Empty settings should be invalid
        }

        response = await client.post(f"{self.base_url}/products/", json=invalid_data)
        assert response.status_code == 422

    async def test_update_product_not_found(self, client: httpx.AsyncClient):
        update_data = {
            "name": "Updated Product Name",
            "description": "Updated description",
        }

        response = await client.put(
            f"{self.base_url}/products/non_existent_id", json=update_data
        )
        assert response.status_code == 404
