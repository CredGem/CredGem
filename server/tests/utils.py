from uuid import uuid4

import httpx

from src.models.wallets import CreateWalletRequest


async def create_credit_type(client: httpx.AsyncClient, base_url: str):
    credit_type_request = {
        "name": "Default Credit Type",
        "description": "Default credit type for product tests",
    }
    response = await client.post(f"{base_url}/credit-types", json=credit_type_request)
    return response.json()


async def create_wallet(client: httpx.AsyncClient, base_url: str):
    user_id = str(uuid4())
    wallet_name = f"test_wallet_{user_id}"
    request = CreateWalletRequest(name=wallet_name, context={"user_id": user_id})
    response = await client.post(f"{base_url}/wallets/", json=request.model_dump())
    return response.json()


async def create_product(
    client: httpx.AsyncClient, base_url: str, settings: list[dict]
):
    product_data = {
        "name": f"Test Product {uuid4()}",
        "description": "A test product",
        "settings": settings,
    }
    response = await client.post(f"{base_url}/products/", json=product_data)
    return response.json()
