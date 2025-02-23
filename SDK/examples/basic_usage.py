import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

from credgem import CredGemClient


async def main():
    # Initialize the client with specific API URL
    # For production, use: https://api.credgem.com
    # For staging: https://api.staging.credgem.com
    # For local development: http://localhost:8000
    async with CredGemClient(
        api_key="your-api-key",
        base_url="http://localhost:8000",  # Explicitly set the API URL
    ) as client:
        # Create a credit type
        credit_type = await client.credit_types.create(
            name="REWARD_POINTS", description="Customer reward points"
        )
        print(f"Created credit type: {credit_type.id}")

        # Create a wallet
        wallet = await client.wallets.create(
            name="Customer Wallet",
            description="Main wallet for customer rewards",
            context={"customer_id": "cust_123"},
        )
        print(f"Created wallet: {wallet.id}")

        # Deposit credits
        deposit = await client.transactions.deposit(
            wallet_id=wallet.id,
            amount=Decimal("100.00"),
            credit_type_id=credit_type.id,
            description="Welcome bonus",
            issuer="system",
            external_transaction_id="welcome_bonus_cust_123",
            context={"source": "welcome_bonus"},
        )
        print(f"Deposited credits: {deposit.id}")

        # Create a hold
        hold = await client.transactions.hold(
            wallet_id=wallet.id,
            amount=Decimal("25.00"),
            credit_type_id=credit_type.id,
            description="Hold for pending purchase",
            issuer="store_app",
            external_transaction_id="purchase_hold_123",
            context={"order_id": "order_123"},
        )
        print(f"Created hold: {hold.id}")

        # Debit using the hold
        debit = await client.transactions.debit(
            wallet_id=wallet.id,
            amount=Decimal("25.00"),
            credit_type_id=credit_type.id,
            description="Purchase completion",
            issuer="store_app",
            hold_transaction_id=hold.id,
            external_transaction_id="purchase_debit_123",
            context={"order_id": "order_123"},
        )
        print(f"Debited credits: {debit.id}")

        # Get wallet details
        updated_wallet = await client.wallets.get(wallet.id)
        print(
            "Current balances:",
            {
                balance.credit_type_id: balance.available
                for balance in updated_wallet.balances
            },
        )

        # Get insights
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # Get wallet activity
        activity = await client.insights.get_wallet_activity(
            wallet_id=wallet.id,
            start_date=start_date,
            end_date=end_date,
            granularity="day",
        )
        print("Wallet activity:", activity.points)

        # List all wallets with pagination
        wallets = await client.wallets.list(page=1, page_size=10)
        print(f"Total wallets: {wallets.total_count}")

        # List transactions for the wallet
        transactions = await client.transactions.list(
            wallet_id=wallet.id, page=1, page_size=10
        )
        print(f"Total transactions: {transactions.total_count}")


if __name__ == "__main__":
    asyncio.run(main())
