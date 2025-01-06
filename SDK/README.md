# CredGem Python SDK

A Python SDK for interacting with the CredGem API.

## Installation

```bash
pip install credgem-sdk
```

## Usage

```python
from credgem import CredGemClient

# Initialize the client
client = CredGemClient(api_key="your-api-key", base_url="https://api.credgem.com")

# Create a wallet
wallet = await client.wallets.create(name="My Wallet")

# Get wallet details
wallet = await client.wallets.get("wallet-id")

# List transactions
transactions = await client.transactions.list(wallet_id="wallet-id")
```

## Features

- Wallet management
- Transaction operations
- Credit type operations
- Insights and analytics
- Async support
- Type hints for better IDE integration

## Documentation

For detailed documentation, visit [docs.credgem.com](https://docs.credgem.com) 