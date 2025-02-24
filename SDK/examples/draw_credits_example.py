import asyncio
from decimal import Decimal

from credgem import CredGemClient
from credgem.exceptions import InsufficientCreditsError
from credgem.models.credit_types import CreditTypeRequest
from credgem.models.transactions import DepositRequest
from credgem.models.wallets import WalletRequest


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
            amount=float(amount),
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
                amount=float(final_amount),
                additional_context={
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


async def main():
    async with CredGemClient(
        api_key="your-api-key", base_url="http://localhost:8000"
    ) as client:
        # Create a credit type
        credit_type = await client.credit_types.create(
            CreditTypeRequest(
                name="STORE_CREDITS", description="Store purchase credits"
            )
        )

        # Create a wallet with initial deposit
        wallet = await client.wallets.create(
            WalletRequest(
                name="Customer Wallet",
                description="Store credits wallet",
                context={"customer_id": "CUST_123"},
            )
        )

        # Add some credits
        await client.transactions.deposit(
            DepositRequest(
                wallet_id=wallet.id,
                amount=float("100.00"),
                credit_type_id=credit_type.id,
                description="Initial deposit",
                issuer="system",
            )
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


if __name__ == "__main__":
    asyncio.run(main())
