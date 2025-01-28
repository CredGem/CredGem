# Getting Started with CredGem SDK

The CredGem SDK provides a simple and intuitive way to integrate credit management into your Python applications. This guide will help you get started with the basic concepts and operations.

## Installation

Install the CredGem SDK using pip:

```bash
pip install credgem-sdk
```

Or if you're using Poetry:

```bash
poetry add credgem-sdk
```

## Basic Usage

Here's a quick example to get you started:

```python
import asyncio
from decimal import Decimal
from credgem import CredGemClient

async def main():
    # Initialize the client
    async with CredGemClient(
        api_key="your-api-key",
        base_url="https://api.credgem.com"  # or your specific API URL
    ) as client:
        # Create a credit type
        credit_type = await client.credit_types.create(
            name="REWARD_POINTS",
            description="Customer reward points"
        )

        # Create a wallet
        wallet = await client.wallets.create(
            name="Customer Wallet",
            description="Main wallet for customer rewards",
            context={"customer_id": "cust_123"}
        )

        # Deposit credits
        await client.transactions.deposit(
            wallet_id=wallet.id,
            amount=Decimal("100.00"),
            credit_type_id=credit_type.id,
            description="Welcome bonus",
            issuer="system"
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Working with Credits

### The DrawCredits Context Manager

The SDK provides a powerful context manager for handling credit operations safely. The `DrawCredits` context manager ensures that credits are properly managed throughout their lifecycle, including automatic cleanup in case of errors or exceptions.

Key features:
- Automatic hold creation when entering the context
- Automatic release of held credits if not debited
- Automatic release on exceptions
- Support for both hold-then-debit and direct debit flows

Here's a basic example:

```python
async def process_purchase(client, wallet_id, credit_type_id, amount):
    async with client.draw_credits(
        wallet_id=wallet_id,
        credit_type_id=credit_type_id,
        amount=Decimal("50.00"),
        description="Purchase with hold",
        issuer="store_app"
    ) as draw:
        # Credits are automatically held here
        
        # Process your order
        success = await process_order()
        
        if success:
            # Debit the held credits
            await draw.debit()
        # If no debit is called, credits are automatically released
```

#### Error Handling and Automatic Release

The context manager automatically handles various scenarios to ensure credits don't get stuck in a held state:

1. **Exception during processing**:
```python
async with client.draw_credits(
    wallet_id=wallet_id,
    credit_type_id=credit_type_id,
    amount=Decimal("50.00"),
    description="Purchase with hold",
    issuer="store_app"
) as draw:
    # Credits are held here
    
    # If any exception occurs here...
    raise RuntimeError("Order processing failed")
    
    # We never reach this point, but the context manager
    # automatically releases the held credits
```

2. **No debit called**:
```python
async with client.draw_credits(
    wallet_id=wallet_id,
    credit_type_id=credit_type_id,
    amount=Decimal("50.00"),
    description="Purchase with hold",
    issuer="store_app"
) as draw:
    # Credits are held here
    
    # If we exit without calling debit(),
    # credits are automatically released
```

3. **Conditional debit**:
```python
async with client.draw_credits(
    wallet_id=wallet_id,
    credit_type_id=credit_type_id,
    amount=Decimal("50.00"),
    description="Purchase with hold",
    issuer="store_app"
) as draw:
    success = await process_order()
    
    if success:
        await draw.debit()  # Credits are debited
    else:
        # No debit called, so credits are automatically released
        # You can also explicitly release:
        await draw.release(context={"reason": "order_failed"})
```

4. **Network errors**:
```python
async with client.draw_credits(
    wallet_id=wallet_id,
    credit_type_id=credit_type_id,
    amount=Decimal("50.00"),
    description="Purchase with hold",
    issuer="store_app"
) as draw:
    try:
        result = await external_api_call()
        await draw.debit()
    except ConnectionError:
        # Credits are automatically released if we don't debit
        logger.error("External API call failed")
```

#### Direct Debit Mode

### Direct Debiting

For simpler cases, you can debit credits directly:

```python
async with client.draw_credits(
    wallet_id=wallet_id,
    credit_type_id=credit_type_id,
    description="Direct purchase",
    issuer="store_app",
    skip_hold=True  # Skip the hold step
) as draw:
    await draw.debit(amount=Decimal("25.00"))
```

## Error Handling

The SDK provides specific exceptions for different error cases:

```python
from credgem.exceptions import InsufficientCreditsError, InvalidRequestError

try:
    async with client.draw_credits(...) as draw:
        await draw.debit()
except InsufficientCreditsError:
    print("Not enough credits available")
except InvalidRequestError as e:
    print(f"Invalid request: {e}")
```

## Working with Wallets

### Creating and Managing Wallets

```python
# Create a wallet
wallet = await client.wallets.create(
    name="Game Wallet",
    description="In-game currency wallet",
    context={"game_id": "game_123", "player_id": "player_456"}
)

# Get wallet details
wallet_info = await client.wallets.get(wallet.id)

# List all wallets
wallets = await client.wallets.list(page=1, page_size=10)
```

### Getting Wallet Insights

```python
from datetime import datetime, timedelta

# Get wallet activity
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

activity = await client.insights.get_wallet_activity(
    wallet_id=wallet.id,
    start_date=start_date,
    end_date=end_date,
    granularity="day"
)

# Get credit usage insights
usage = await client.insights.get_credit_usage(
    wallet_id=wallet.id,
    start_date=start_date,
    end_date=end_date,
    granularity="day"
)
```

## Best Practices

1. **Always use context managers**: The `DrawCredits` context manager ensures proper cleanup of held credits.

2. **Use idempotency keys**: For critical operations, provide transaction IDs to ensure idempotency:
   ```python
   async with client.draw_credits(
       wallet_id=wallet_id,
       credit_type_id=credit_type_id,
       amount=amount,
       transaction_id="unique_transaction_id",
       ...
   ) as draw:
       await draw.debit()
   ```

3. **Handle errors appropriately**: Always catch and handle specific exceptions.

4. **Clean up resources**: Use async context managers to ensure proper cleanup:
   ```python
   async with CredGemClient(...) as client:
       # Your code here
   # Client is automatically cleaned up
   ```

## Environment Configuration

The SDK supports different environments:

```python
# Production
client = CredGemClient(
    api_key="your-api-key",
    base_url="https://api.credgem.com"
)

# Staging
client = CredGemClient(
    api_key="your-staging-key",
    base_url="https://api.staging.credgem.com"
)

# Local development
client = CredGemClient(
    api_key="your-dev-key",
    base_url="http://localhost:8000"
)
```

## Next Steps

- Check out our [API Reference](https://docs.credgem.com/api) for detailed documentation
- View example implementations in our [GitHub repository](https://github.com/credgem/credgem-python/tree/main/examples)
- Join our [Discord community](https://discord.gg/credgem) for support and discussions 