import asyncio
from decimal import Decimal
from credgem import CredGemClient
from credgem.exceptions import InsufficientCreditsError


async def process_order(
    client: CredGemClient,
    wallet_id: str,
    credit_type_id: str,
    order_id: str,
    amount: Decimal,
):
    try:
        # Use DrawCredits context to handle the credit flow
        async with client.draw_credits(
            wallet_id=wallet_id,
            credit_type_id=credit_type_id,
            amount=amount,
            description=f"Processing order {order_id}",
            issuer="order_system",
            context={
                "order_id": order_id,
                "order_type": "purchase",
                "customer_reference": "REF123",
            },
        ) as draw:
            # Simulate order processing
            await asyncio.sleep(1)
            print(f"Processing order {order_id}...")

            # Simulate some business logic that might change the final amount
            final_amount = amount * Decimal("0.95")  # 5% discount

            # Explicitly debit with the final amount and additional context
            await draw.debit(
                amount=final_amount,
                context={
                    "discount_applied": "5%",
                    "original_amount": str(amount),
                    "status": "completed",
                },
            )
            print(f"Order {order_id} processed successfully with amount {final_amount}")

    except InsufficientCreditsError:
        print(f"Insufficient credits for order {order_id}")
        return False
    except Exception as e:
        print(f"Error processing order {order_id}: {e}")
        return False

    return True


async def process_order_with_manual_release(
    client: CredGemClient,
    wallet_id: str,
    credit_type_id: str,
    order_id: str,
    amount: Decimal,
):
    try:
        async with client.draw_credits(
            wallet_id=wallet_id,
            credit_type_id=credit_type_id,
            amount=amount,
            description=f"Processing order {order_id}",
            issuer="order_system",
            context={"order_id": order_id},
        ) as draw:
            # Simulate order processing that fails
            await asyncio.sleep(1)
            print(f"Processing order {order_id}...")

            success = False  # Simulate failure

            if success:
                await draw.debit(context={"status": "completed"})
            else:
                # Explicitly release the hold with failure context
                await draw.release(
                    context={"status": "failed", "reason": "order_processing_failed"}
                )
                print(f"Order {order_id} failed, hold released")
                return False

    except Exception as e:
        print(f"Error processing order {order_id}: {e}")
        return False

    return True


async def main():
    async with CredGemClient(
        api_key="your-api-key", base_url="http://localhost:8000"
    ) as client:
        # Create a credit type
        credit_type = await client.credit_types.create(
            name="STORE_CREDITS", description="Store purchase credits"
        )

        # Create a wallet with initial deposit
        wallet = await client.wallets.create(
            name="Customer Wallet",
            description="Store credits wallet",
            context={"customer_id": "CUST_123"},
        )

        # Add some credits
        await client.transactions.deposit(
            wallet_id=wallet.id,
            amount=Decimal("100.00"),
            credit_type_id=credit_type.id,
            description="Initial deposit",
            issuer="system",
        )

        # Process orders with automatic discount
        orders = [
            ("ORDER_001", "50.00"),  # Will be charged 47.50
            ("ORDER_002", "30.00"),  # Will be charged 28.50
        ]

        for order_id, amount in orders:
            success = await process_order(
                client,
                wallet_id=wallet.id,
                credit_type_id=credit_type.id,
                order_id=order_id,
                amount=Decimal(amount),
            )
            print(f"Order {order_id} {'succeeded' if success else 'failed'}")

            # Check wallet balance after each order
            wallet_info = await client.wallets.get(wallet.id)
            for balance in wallet_info.balances:
                if balance.credit_type_id == credit_type.id:
                    print(f"Current balance: {balance.available}")

        # Process an order that will fail and demonstrate manual release
        await process_order_with_manual_release(
            client,
            wallet_id=wallet.id,
            credit_type_id=credit_type.id,
            order_id="ORDER_003",
            amount=Decimal("20.00"),
        )


if __name__ == "__main__":
    asyncio.run(main())
