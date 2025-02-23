import asyncio
from decimal import Decimal

from credgem import CredGemClient
from credgem.exceptions import InsufficientCreditsError

# Example environment-specific configurations
ENVIRONMENTS = {
    "production": {
        "api_url": "https://api.credgem.com",
        "api_key": "your_production_key",
    },
    "staging": {
        "api_url": "https://api.staging.credgem.com",
        "api_key": "your_staging_key",
    },
    "development": {"api_url": "http://localhost:8000", "api_key": "your_dev_key"},
}

# Choose environment
ENVIRONMENT = "development"  # Change this to switch environments


async def scenario_1_success_with_hold(client: CredGemClient):
    """Scenario 1: Success flow with hold and debit"""
    print("\nScenario 1: Success flow with hold and debit")

    async with client.draw_credits(
        wallet_id="wallet_123",
        credit_type_id="POINTS",
        amount=Decimal("50.00"),
        description="Purchase with hold",
        issuer="store_app",
        context={"order_id": "order_123"},
    ) as draw:
        # Simulate order processing
        print("Processing order...")
        await asyncio.sleep(1)

        # Complete the purchase with debit
        await draw.debit(context={"status": "completed"})
        print("Order completed successfully")


async def scenario_2_direct_debit(client: CredGemClient):
    """Scenario 2: Direct debit without hold"""
    print("\nScenario 2: Direct debit without hold")

    async with client.draw_credits(
        wallet_id="wallet_123",
        credit_type_id="POINTS",
        description="Direct purchase",
        issuer="store_app",
        skip_hold=True,  # Skip the hold step
        context={"order_id": "order_124"},
    ) as draw:
        # Perform direct debit
        await draw.debit(amount=Decimal("25.00"), context={"status": "completed"})
        print("Direct debit completed successfully")


async def scenario_3_exception_handling(client: CredGemClient):
    """Scenario 3: Exception in context body - automatic release"""
    print("\nScenario 3: Exception handling with automatic release")

    try:
        async with client.draw_credits(
            wallet_id="wallet_123",
            credit_type_id="POINTS",
            amount=Decimal("75.00"),
            description="Failed purchase",
            issuer="store_app",
            context={"order_id": "order_125"},
        ) as draw:
            print("Processing order...")
            await asyncio.sleep(1)

            # Simulate an error
            raise ValueError("Payment processing failed")

    except ValueError as e:
        print(f"Order failed: {e}")
        print("Hold was automatically released")


async def scenario_4_no_debit_called(client: CredGemClient):
    """Scenario 4: No debit called - hold remains until exit"""
    print("\nScenario 4: No debit called - automatic release")

    async with client.draw_credits(
        wallet_id="wallet_123",
        credit_type_id="POINTS",
        amount=Decimal("30.00"),
        description="Abandoned purchase",
        issuer="store_app",
        context={"order_id": "order_126"},
    ) as draw:
        print("Processing order...")
        await asyncio.sleep(1)

        print("Order abandoned without debit")
        # Don't call debit - hold will be automatically released

    print("Hold was automatically released")


async def scenario_5_retry_with_idempotency(client: CredGemClient):
    """Scenario 5: Retry operation with same transaction ID"""
    print("\nScenario 5: Retry with idempotency")

    transaction_id = "tx_retry_123"

    # First attempt
    try:
        async with client.draw_credits(
            wallet_id="wallet_123",
            credit_type_id="POINTS",
            amount=Decimal("40.00"),
            description="Retry purchase",
            issuer="store_app",
            transaction_id=transaction_id,
            context={"order_id": "order_127"},
        ) as draw:
            print("First attempt...")
            await draw.debit()
            print("First attempt completed")
    except Exception:
        print("First attempt failed")

    # Retry with same transaction ID
    async with client.draw_credits(
        wallet_id="wallet_123",
        credit_type_id="POINTS",
        amount=Decimal("40.00"),
        description="Retry purchase",
        issuer="store_app",
        transaction_id=transaction_id,  # Same transaction ID
        context={"order_id": "order_127"},
    ) as draw:
        print("Retrying...")
        await draw.debit()
        print("Retry completed (409 Conflict means it was already processed)")


async def main():
    # Get environment configuration
    env_config = ENVIRONMENTS[ENVIRONMENT]

    print(f"Connecting to {env_config['api_url']}")
    async with CredGemClient(
        api_key=env_config["api_key"], base_url=env_config["api_url"]
    ) as client:
        # Create a credit type for testing
        credit_type = await client.credit_types.create(
            name="POINTS", description="Test points"
        )

        # Create a wallet with initial balance
        wallet = await client.wallets.create(
            name="Test Wallet", context={"customer_id": "cust_123"}
        )

        # Add initial credits
        await client.transactions.deposit(
            wallet_id=wallet.id,
            amount=Decimal("1000.00"),
            credit_type_id=credit_type.id,
            description="Initial deposit",
            issuer="system",
        )

        # Run all scenarios
        scenarios = [
            scenario_1_success_with_hold,
            scenario_2_direct_debit,
            scenario_3_exception_handling,
            scenario_4_no_debit_called,
            scenario_5_retry_with_idempotency,
        ]

        for scenario in scenarios:
            try:
                await scenario(client)

                # Check wallet balance after each scenario
                wallet_info = await client.wallets.get(wallet.id)
                for balance in wallet_info.balances:
                    if balance.credit_type_id == credit_type.id:
                        print(f"Current balance: {balance.available}")
                        print(f"Held amount: {balance.held}")

            except Exception as e:
                print(f"Scenario failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
