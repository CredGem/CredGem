# CredGem Python SDK

A Python SDK for interacting with the CredGem API. Manage digital credits, wallets, and transactions with a simple, intuitive interface.

[![GitHub](https://img.shields.io/badge/GitHub-CredGem%2FCredGem-blue?logo=github)](https://github.com/CredGem/CredGem)

## Features

- 🏦 Wallet management
- 💳 Transaction operations (deposits, holds, debits)
- 🏷️ Credit type operations
- 📊 Insights and analytics
- ⚡ Async support with context managers
- 🔍 Type hints for better IDE integration
- 🔄 Automatic hold release on errors
- 🎯 Idempotent operations
- ⚙️ Environment-specific configurations

## Installation

```bash
pip install credgem-sdk
```

## Quick Start

```python
from credgem import CredGemClient
from decimal import Decimal

async with CredGemClient(api_key="your-api-key") as client:
    # Create a wallet
    wallet = await client.wallets.create(
        name="Customer Wallet",
        context={"customer_id": "cust_123"}
    )
    
    # Deposit credits
    await client.transactions.deposit(
        wallet_id=wallet.id,
        amount=100.00,
        credit_type_id="POINTS",
        description="Welcome bonus"
    )
    
    # Check balance
    balance = await client.wallets.get_balance(wallet.id)
    print(f"Wallet balance: {balance.available_amount} {balance.credit_type_id}")
```

## Configuration

Configure the SDK for different environments:

```python
from credgem import CredGemClient

# Production
client = CredGemClient(
    api_key="your-api-key",
    base_url="https://api.credgem.com"  # Default
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

## Transaction Operations

### Deposits

```python
await client.transactions.deposit(
    wallet_id=wallet.id,
    amount=100.00,
    credit_type_id="POINTS",
    description="Welcome bonus",
    issuer="system",
    external_id="welcome_bonus_123",  # For idempotency
    context={"source": "welcome_bonus"}
)
```

### Holds and Debits

Use the `draw_credits` context manager for safe credit operations:

```python
# Hold and debit pattern
async with client.draw_credits(
    wallet_id=wallet.id,
    credit_type_id="POINTS",
    amount=50.00,
    description="Purchase with hold",
    issuer="store_app",
    context={"order_id": "order_123"}
) as draw:
    # Process your order here
    order_success = await process_order()
    
    if order_success:
        await draw.debit()  # Completes the transaction
    # Hold is automatically released if no debit is called
```

### Direct Debits

For immediate debits without holds:

```python
async with client.draw_credits(
    wallet_id=wallet.id,
    credit_type_id="POINTS",
    description="Direct purchase",
    issuer="store_app",
    skip_hold=True
) as draw:
    await draw.debit(amount=25.00)
```

### Manual Hold Operations

For more control over the hold process:

```python
# Create a hold
hold = await client.transactions.hold(
    wallet_id=wallet.id,
    amount=25.00,
    credit_type_id="POINTS",
    description="Hold for pending purchase"
)

# Release a hold
await client.transactions.release(
    wallet_id=wallet.id,
    hold_transaction_id=hold.id,
    description="Release pending hold"
)

# Debit against a hold
await client.transactions.debit(
    wallet_id=wallet.id,
    amount=25.00,
    credit_type_id="POINTS",
    description="Purchase completion",
    hold_transaction_id=hold.id
)
```

## Wallet Operations

```python
# Create a wallet
wallet = await client.wallets.create(
    name="My Wallet",
    context={"customer_id": "cust_123"}
)

# Get wallet details
wallet = await client.wallets.get(wallet.id)

# List transactions
transactions = await client.transactions.list(
    wallet_id=wallet.id,
    limit=10,
    offset=0
)

# Get wallet balance
balance = await client.wallets.get_balance(
    wallet_id=wallet.id,
    credit_type_id="POINTS"
)
```

## Error Handling

The SDK provides clear error messages and proper exception handling:

```python
from credgem.exceptions import InsufficientCreditsError, WalletNotFoundError

try:
    async with client.draw_credits(...) as draw:
        await draw.debit(amount=1000.00)
except InsufficientCreditsError:
    print("Not enough credits available")
except InvalidRequestError:
    print("Invalid request")
```

## Documentation

For detailed documentation, API reference, and more examples, visit:
- [Official Documentation](https://docs.credgem.com)
- [API Reference](https://docs.credgem.com/api)

## Support

- 📧 Email: support@credgem.com
- 💬 Discord: [Join our community](https://discord.gg/credgem)
- 🐛 Issues: [GitHub Issues](https://github.com/CredGem/CredGem/issues) 