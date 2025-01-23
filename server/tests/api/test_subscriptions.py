import asyncio
from uuid import uuid4

import httpx
import pytest
from pydantic import BaseModel

from src.core.settings import settings
from src.models.products import (
    ProductSubscriptionRequest,
    SubscriptionMode,
    SubscriptionStatus,
    SubscriptionType,
)
from tests import utils as test_utils

pytestmark = pytest.mark.anyio


class ProductSetup(BaseModel):
    credit_type: dict
    wallet: dict
    product: dict


class TestSubscriptions:
    base_url = settings.API_V1_STR

    @pytest.fixture(scope="function")
    async def setup_product(self, client: httpx.AsyncClient):
        credit_type, second_credit_type = await asyncio.gather(
            test_utils.create_credit_type(client, self.base_url),
            test_utils.create_credit_type(client, self.base_url),
        )
        wallet = await test_utils.create_wallet(client, self.base_url)
        settings = [
            {"credit_type_id": credit_type["id"], "credit_amount": 100.0},
            {"credit_type_id": second_credit_type["id"], "credit_amount": 200.0},
        ]
        product = await test_utils.create_product(client, self.base_url, settings)

        return ProductSetup(
            credit_type=credit_type,
            wallet=wallet,
            product=product,
        )

    def _find_balance_by_credit_type_id(
        self, wallet: dict, credit_type_id: str
    ) -> dict | None:
        for balance in wallet["balances"]:
            if balance["credit_type_id"] == credit_type_id:
                return balance
        return None

    async def test_create_one_time_add_subscription(
        self, client: httpx.AsyncClient, setup_product: ProductSetup
    ):
        wallet_id = setup_product.wallet["id"]
        subscription_request = ProductSubscriptionRequest(
            product_id=setup_product.product["id"],
            type=SubscriptionType.ONE_TIME,
            mode=SubscriptionMode.ADD,
        )
        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/subscriptions/",
            json=subscription_request.model_dump(),
        )
        assert response.status_code == 200
        subscription = response.json()
        assert subscription["status"] == SubscriptionStatus.COMPLETED

        # get wallet
        response = await client.get(f"{self.base_url}/wallets/{wallet_id}")
        assert response.status_code == 200
        wallet = response.json()

        for setting in setup_product.product["settings"]:
            balance = self._find_balance_by_credit_type_id(
                wallet, setting["credit_type_id"]
            )
            assert balance is not None
            assert balance["available"] == setting["credit_amount"]

    async def test_create_subscription_non_existing_product(
        self, client: httpx.AsyncClient
    ):
        wallet = await test_utils.create_wallet(client, self.base_url)
        subscription_request = ProductSubscriptionRequest(
            product_id=str(uuid4()),
            type=SubscriptionType.ONE_TIME,
            mode=SubscriptionMode.ADD,
        )
        response = await client.post(
            f"{self.base_url}/wallets/{wallet['id']}/subscriptions/",
            json=subscription_request.model_dump(),
        )
        assert response.status_code == 404

    async def test_get_subscriptions(
        self, client: httpx.AsyncClient, setup_product: ProductSetup
    ):
        wallet_id = setup_product.wallet["id"]
        subscription_request = ProductSubscriptionRequest(
            product_id=setup_product.product["id"],
            type=SubscriptionType.ONE_TIME,
            mode=SubscriptionMode.ADD,
        )
        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/subscriptions/",
            json=subscription_request.model_dump(),
        )
        assert response.status_code == 200
        subscription = response.json()
        assert subscription["status"] == SubscriptionStatus.COMPLETED

        response = await client.get(
            f"{self.base_url}/wallets/{wallet_id}/subscriptions/"
        )
        assert response.status_code == 200
        subscription_response = response.json()
        assert subscription_response["total_count"] == 1
        subscription_data = subscription_response["data"][0]
        assert subscription_data["status"] == SubscriptionStatus.COMPLETED
        assert subscription_data["product"]["id"] == setup_product.product["id"]
