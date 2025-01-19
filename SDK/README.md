# CredGem Python SDK

A Python SDK for interacting with the CredGem API.

## Installation

```bash
pip install credgem-sdk
```

## Configuration

The SDK can be configured to work with different environments:

```python
from credgem import CredGemClient

# Production environment
client = CredGemClient(
    api_key="your-api-key",
    base_url="https://api.credgem.com"
)

# Staging environment
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

## Basic Usage

```python
from credgem import CredGemClient
from decimal import Decimal

async with CredGemClient(api_key="your-api-key", base_url="https://api.credgem.com") as client:
    # Create a wallet
    wallet = await client.wallets.create(
        name="My Wallet",
        context={"customer_id": "cust_123"}
    )

    # Get wallet details
    wallet = await client.wallets.get(wallet.id)

    # List transactions
    transactions = await client.transactions.list(wallet_id=wallet.id)
```

## Credit Operations

The SDK provides a context manager for safe credit operations:

```python
# With hold and debit
async with client.draw_credits(
    wallet_id="wallet_123",
    credit_type_id="POINTS",
    amount=Decimal("50.00"),
    description="Purchase with hold",
    issuer="store_app",
    context={"order_id": "order_123"}
) as draw:
    # Process your order
    result = await process_order()
    if result.success:
        await draw.debit()  # Uses held amount
    # If no debit is called, hold is automatically released

# Direct debit without hold
async with client.draw_credits(
    wallet_id="wallet_123",
    credit_type_id="POINTS",
    description="Direct purchase",
    issuer="store_app",
    skip_hold=True
) as draw:
    await draw.debit(amount=Decimal("25.00"))
```

## Features

- Wallet management
- Transaction operations
- Credit type operations
- Insights and analytics
- Async support
- Type hints for better IDE integration
- Automatic hold release on errors
- Idempotent operations
- Environment-specific configurations

## Documentation

For detailed documentation, visit [docs.credgem.com](https://docs.credgem.com) 