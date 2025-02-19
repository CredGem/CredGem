import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict
from httpx import HTTPStatusError

from credgem import CredGemClient
from credgem.api.insights import TimeGranularity


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
                name=name, description=description
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
            name=f"Customer {customer_id} Wallet",
            context={"customer_id": customer_id, "type": "customer", "tier": "gold"},
        )

        # Initial deposits for each credit type
        deposits = [
            ("POINTS", "100.00", "Welcome points"),
            ("BONUS", "50.00", "Sign-up bonus"),
            ("PROMO", "25.00", "First-time promo"),
        ]

        for credit_type, amount, description in deposits:
            await client.transactions.deposit(
                wallet_id=wallet.id,
                amount=float(amount),
                credit_type_id=credit_types[credit_type],
                description=description,
                issuer="onboarding_system",
                idempotency_key=f"welcome_{customer_id}_{credit_type}",
                context={"event": "customer_onboarding"},
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
) -> bool:
    """Process a purchase with hold and debit"""
    try:
        # Create hold
        hold = await client.transactions.hold(
            wallet_id=wallet_id,
            amount=float(amount),
            credit_type_id=credit_type_id,
            description=f"Hold for order {order_id}",
            issuer="purchase_system",
            external_transaction_id=f"hold_{order_id}",
            context={"order_id": order_id, "type": "purchase"},
        )

        # Simulate some processing time
        await asyncio.sleep(1)

        # Complete the purchase with debit
        await client.transactions.debit(
            wallet_id=wallet_id,
            amount=float(amount),
            credit_type_id=credit_type_id,
            description=f"Purchase for order {order_id}",
            issuer="purchase_system",
            hold_transaction_id=hold.id,
            external_transaction_id=f"debit_{order_id}",
            context={"order_id": order_id, "type": "purchase"},
        )

        return True
    except HTTPStatusError as e:
        print(f"Failed to process purchase: {e}")
        # If hold was created but debit failed, release the hold
        if "hold" in locals():
            try:
                await client.transactions.release(
                    wallet_id=wallet_id,
                    hold_transaction_id=hold.id,
                    credit_type_id=credit_type_id,
                    description=f"Release failed purchase hold for order {order_id}",
                    issuer="purchase_system",
                    idempotency_key=f"release_{order_id}",
                    context={"order_id": order_id, "type": "purchase_failed"},
                )
            except HTTPStatusError as release_error:
                print(f"Failed to release hold: {release_error}")
        return False


async def get_wallet_statistics(client: CredGemClient, wallet_id: str) -> Dict:
    """Get comprehensive wallet statistics"""
    try:
        # Get current wallet state
        wallet = await client.wallets.get(wallet_id)

        # Get historical activity
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        activity = await client.insights.get_wallet_activity(
            wallet_id=wallet_id,
            start_date=start_date,
            end_date=end_date,
            granularity=TimeGranularity.DAY,
        )

        credit_usage = await client.insights.get_credit_usage(
            wallet_id=wallet_id,
            start_date=start_date,
            end_date=end_date,
            granularity=TimeGranularity.DAY,
        )

        return {
            "current_balances": {
                balance.credit_type_id: {
                    "available": balance.available,
                    "held": balance.held,
                    "spent": balance.spent,
                }
                for balance in wallet.balances
            },
            "activity_summary": {
                "total_transactions": sum(
                    point.total_transactions for point in activity.points
                ),
                "total_deposits": sum(
                    point.total_deposits for point in activity.points
                ),
                "total_debits": sum(point.total_debits for point in activity.points),
            },
            "credit_usage": {
                point.credit_type_id: {
                    "transactions": point.transaction_count,
                    "amount": point.debits_amount,
                }
                for point in credit_usage.points
            },
        }
    except HTTPStatusError as e:
        print(f"Failed to get wallet statistics: {e}")
        return {}


async def main():
    async with CredGemClient(
        api_key="your-api-key", base_url="http://localhost:8000"
    ) as client:
        # Set up credit types
        credit_types = await setup_credit_types(client)

        # Create customer wallet
        wallet_id = await create_customer_wallet(
            client, customer_id="CUST_123", credit_types=credit_types
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
            )
            print(f"Purchase {order_id} {'succeeded' if success else 'failed'}")

        # Get and print statistics
        stats = await get_wallet_statistics(client, wallet_id)
        print("\nWallet Statistics:")
        print("Current Balances:", stats["current_balances"])
        print("Activity Summary:", stats["activity_summary"])
        print("Credit Usage:", stats["credit_usage"])


if __name__ == "__main__":
    asyncio.run(main())
