import argparse
import asyncio
from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4

from sqlalchemy import text

from scripts.seed_data import generate_seed_data
from src.core.db_config import DBManager
from src.models.balances import BalanceDBModel
from src.models.transactions import TransactionDBModel, TransactionType
from src.utils.ctx_managers import db_session


async def calculate_balances(
    transactions: List[TransactionDBModel],
) -> List[BalanceDBModel]:
    """Calculate final balances based on transactions."""
    balances: Dict[str, BalanceDBModel] = {}

    for tx in sorted(transactions, key=lambda x: x.created_at):
        key = f"{tx.wallet_id}_{tx.credit_type_id}"
        if key not in balances:
            balances[key] = BalanceDBModel(
                id=str(uuid4()),
                wallet_id=tx.wallet_id,
                credit_type_id=tx.credit_type_id,
                available=0.0,
                held=0.0,
                spent=0.0,
                overall_spent=0.0,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )

        amount = tx.payload.get("amount", 0)

        if tx.type == TransactionType.DEPOSIT:
            balances[key].available += amount
        elif tx.type == TransactionType.DEBIT:
            balances[key].spent += amount
            balances[key].overall_spent += amount
            if hasattr(tx.payload, "hold_transaction_id"):
                balances[key].held -= amount
            else:
                balances[key].available -= amount
        elif tx.type == TransactionType.HOLD:
            balances[key].held += amount
            balances[key].available -= amount
        elif tx.type == TransactionType.RELEASE:
            balances[key].held -= amount
            balances[key].available += amount

    return list(balances.values())


async def load_seed_data(clear_existing: bool = False):
    """Load the generated seed data into PostgreSQL.

    Args:
        clear_existing: If True, truncates existing tables before seeding
    """
    async with db_session() as session_ctx:
        session = session_ctx.session
        # Optionally clear existing data
        if clear_existing:
            tables = ["credit_types", "wallets", "transactions", "balances"]
            for table in tables:
                await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
            await session.commit()
            print("Existing tables truncated.")

        # Generate seed data
        print("Generating seed data...")
        seed_data = generate_seed_data()

        # Insert credit types
        if seed_data.credit_types:
            session.add_all(seed_data.credit_types)
            await session.flush()

        # Insert wallets
        if seed_data.wallets:
            session.add_all(seed_data.wallets)
            await session.flush()
        # Insert transactions
        if seed_data.transactions:
            session.add_all(seed_data.transactions)
            await session.flush()
        # Calculate and insert balances
        print("Calculating balances...")
        balances = await calculate_balances(seed_data.transactions)
        if balances:
            session.add_all(balances)
            await session.flush()


async def main():
    parser = argparse.ArgumentParser(description="Load seed data into MongoDB")
    parser.add_argument(
        "--clear", action="store_true", help="Clear existing collections before seeding"
    )
    args = parser.parse_args()

    print("Initializing database connection...")
    await DBManager().init_db_connection()

    await load_seed_data(clear_existing=args.clear)
    print("Seed data loaded successfully!")
    print("Disconnecting from database...")
    await DBManager().disconnect()


if __name__ == "__main__":
    asyncio.run(main())
