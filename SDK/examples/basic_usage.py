import asyncio
import uuid

from credgem import CredGemClient
from credgem.models.credit_types import CreditTypeRequest
from credgem.models.transactions import DebitRequest, DepositRequest, HoldRequest
from credgem.models.wallets import WalletRequest


async def main():
    # Initialize the client with specific API URL
    # For production, use: https://api.credgem.com
    # For staging: https://api.staging.credgem.com
    # For local development: http://localhost:8000
    async with CredGemClient(
        api_key="your-api-key",
        base_url="http://localhost:8000/api/v1",  # Explicitly set the API URL
    ) as client:
        # Create a credit type
        _id = str(uuid.uuid4())
        credit_type = await client.credit_types.create(
            CreditTypeRequest(
                name=f"REWARD_POINTS_{_id}", description="Customer reward points"
            )
        )
        print(f"Created credit type: {credit_type.id}")

        # Create a wallet
        wallet = await client.wallets.create(
            WalletRequest(
                name=f"Customer Wallet_{_id}",
                description="Main wallet for customer rewards",
                context={"customer_id": "cust_123"},
            )
        )
        print(f"Created wallet: {wallet.id}")

        # Deposit credits
        deposit = await client.transactions.deposit(
            DepositRequest(
                wallet_id=wallet.id,
                amount=float("100.00"),
                credit_type_id=credit_type.id,
                description="Welcome bonus",
                issuer="system",
                external_id=f"welcome_bonus_cust_123_{_id}",
                context={"source": "welcome_bonus"},
            )
        )
        print(f"Deposited credits: {deposit.id}")

        # Create a hold
        hold = await client.transactions.hold(
            HoldRequest(
                wallet_id=wallet.id,
                amount=float("25.00"),
                credit_type_id=credit_type.id,
                description="Hold for pending purchase",
                issuer="store_app",
                external_id=f"purchase_hold_123_{_id}",
                context={"order_id": "order_123"},
            )
        )
        print(f"Created hold: {hold.id}")

        # Debit using the hold
        debit = await client.transactions.debit(
            DebitRequest(
                wallet_id=wallet.id,
                amount=float("25.00"),
                credit_type_id=credit_type.id,
                description="Purchase completion",
                issuer="store_app",
                hold_transaction_id=hold.id,
                external_id=f"purchase_debit_123_{_id}",
                context={"order_id": "order_123"},
            )
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
        # List all wallets with pagination
        wallets = await client.wallets.list(page=1, page_size=10)
        print(f"Total wallets: {wallets.total_count}")

        # List transactions for the wallet
        transactions = await client.transactions.list(
            wallet_id=wallet.id, page=1, page_size=10
        )
        print(f"Total transactions: {len(transactions)}")


if __name__ == "__main__":
    asyncio.run(main())
