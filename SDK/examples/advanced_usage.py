import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict
import uuid

from httpx import HTTPStatusError

from credgem import CredGemClient
from credgem.models.credit_types import CreditTypeRequest
from credgem.models.insights import TimeGranularity
from credgem.models.transactions import (
    DebitRequest,
    DepositRequest,
    HoldRequest,
    ReleaseRequest,
)
from credgem.models.wallets import WalletRequest


async def setup_credit_types(client: CredGemClient) -> Dict[str, str]:
    """Set up multiple credit types and return their IDs"""
    credit_types = {}
    types_to_create = [
        ("POINTS", "Regular reward points"),
        ("BONUS", "Special bonus points"),
        ("PROMO", "Promotional credits"),
    ]

    for name, description in types_to_create:
        try:
            credit_type = await client.credit_types.create(
                CreditTypeRequest(name=name, description=description)
            )
            credit_types[name] = credit_type.id
            print(f"Created credit type {name}: {credit_type.id}")
        except HTTPStatusError as e:
            print(f"Failed to create credit type {name}: {e}")

    return credit_types


async def create_customer_wallet(
    client: CredGemClient, customer_id: str, credit_types: Dict[str, str]
) -> str:
    """Create a wallet for a customer with initial deposits"""
    try:
        # Create wallet
        wallet = await client.wallets.create(
            WalletRequest(
                name=f"Customer {customer_id} Wallet",
                description="Multi-currency customer wallet",
                context={
                    "customer_id": customer_id,
                    "type": "customer",
                    "tier": "gold",
                },
            )
        )

        # Initial deposits for each credit type
        deposits = [
            ("POINTS", "100.00", "Welcome points"),
            ("BONUS", "50.00", "Sign-up bonus"),
            ("PROMO", "25.00", "First-time promo"),
        ]

        for credit_type, amount, description in deposits:
            await client.transactions.deposit(
                DepositRequest(
                    wallet_id=wallet.id,
                    amount=float(amount),
                    credit_type_id=credit_types[credit_type],
                    description=description,
                    issuer="onboarding_system",
                    external_id=f"welcome_{customer_id}_{credit_type}",
                    context={"event": "customer_onboarding"},
                )
            )

        return wallet.id
    except HTTPStatusError as e:
        print(f"Failed to set up customer wallet: {e}")
        raise


async def process_purchase(
    client: CredGemClient,
    wallet_id: str,
    credit_type_id: str,
    amount: Decimal,
    order_id: str,
    _id: str,
) -> bool:
    """Process a purchase with hold and debit"""
    try:
        # Create hold
        hold = await client.transactions.hold(
            HoldRequest(
                wallet_id=wallet_id,
                amount=float(amount),
                credit_type_id=credit_type_id,
                description=f"Hold for order {order_id}",
                issuer="purchase_system",
                external_id=f"hold_{order_id}_{_id}",
                context={"order_id": order_id, "type": "purchase"},
            )
        )

        # Simulate some processing time
        await asyncio.sleep(1)

        # Complete the purchase with debit
        await client.transactions.debit(
            DebitRequest(
                wallet_id=wallet_id,
                amount=float(amount),
                credit_type_id=credit_type_id,
                description=f"Purchase for order {order_id}",
                issuer="purchase_system",
                hold_transaction_id=hold.id,
                external_id=f"debit_{order_id}_{_id}",
                context={"order_id": order_id, "type": "purchase"},
            )
        )

        return True
    except HTTPStatusError as e:
        print(f"Failed to process purchase: {e}")
        # If hold was created but debit failed, release the hold
        if "hold" in locals():
            try:
                await client.transactions.release(
                    ReleaseRequest(
                        wallet_id=wallet_id,
                        hold_transaction_id=hold.id,
                        credit_type_id=credit_type_id,
                        description=f"Release failed purchase hold for order {order_id}",
                        issuer="purchase_system",
                        external_id=f"release_{order_id}_{_id}",
                        context={"order_id": order_id, "type": "purchase_failed"},
                    )
                )
            except HTTPStatusError as release_error:
                print(f"Failed to release hold: {release_error}")
        return False


async def main():
    async with CredGemClient(
        api_key="your-api-key", base_url="http://localhost:8000/api/v1"
    ) as client:
        # Set up credit types
        _id = str(uuid.uuid4())
        credit_types = await setup_credit_types(client)

        # Create customer wallet
        wallet_id = await create_customer_wallet(
            client, customer_id=f"CUST_123_{_id}", credit_types=credit_types
        )

        # Process some purchases
        purchases = [
            ("POINTS", "25.00", "ORDER_001"),
            ("BONUS", "10.00", "ORDER_002"),
            ("PROMO", "5.00", "ORDER_003"),
        ]

        for credit_type, amount, order_id in purchases:
            success = await process_purchase(
                client,
                wallet_id=wallet_id,
                credit_type_id=credit_types[credit_type],
                amount=Decimal(amount),
                order_id=order_id,
                _id=_id,
            )
            print(f"Purchase {order_id} {'succeeded' if success else 'failed'}")


if __name__ == "__main__":
    asyncio.run(main())
