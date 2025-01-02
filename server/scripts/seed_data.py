import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from src.models.credit_types import CreditType
from src.models.transactions import (
    DebitTransactionRequestPayload,
    DepositTransactionRequestPayload,
    HoldStatus,
    HoldTransactionRequestPayload,
    ReleaseTransactionRequestPayload,
    TransactionDBModel,
    TransactionRequestPayload,
    TransactionStatus,
    TransactionType,
)
from src.models.wallets import Wallet


class SeedData(BaseModel):
    credit_types: List[CreditType]
    wallets: List[Wallet]
    transactions: List[TransactionDBModel]

    model_config = ConfigDict(arbitrary_types_allowed=True)


# Generate ObjectIDs for credit types
CREDIT_TYPE_IDS = [str(uuid.uuid4()) for _ in range(4)]

ONE_YEAR_AGO = datetime.now(timezone.utc) - timedelta(days=365)

CREDIT_TYPE_SAMPLES = [
    CreditType(
        id=CREDIT_TYPE_IDS[0],
        name="Premium Credits",
        description="Credits for premium features and services",
        created_at=ONE_YEAR_AGO,
        updated_at=ONE_YEAR_AGO,
    ),
    CreditType(
        id=CREDIT_TYPE_IDS[1],
        name="Basic Credits",
        description="Credits for basic features",
        created_at=ONE_YEAR_AGO,
        updated_at=ONE_YEAR_AGO,
    ),
    CreditType(
        id=CREDIT_TYPE_IDS[2],
        name="Service Credits",
        description="Credits for service features",
        created_at=ONE_YEAR_AGO,
        updated_at=ONE_YEAR_AGO,
    ),
    CreditType(
        id=CREDIT_TYPE_IDS[3],
        name="Subscription Credits",
        description="Credits for subscription features",
        created_at=ONE_YEAR_AGO,
        updated_at=ONE_YEAR_AGO,
    ),
]

# Generate ObjectIDs for wallets
WALLET_IDS = [str(uuid.uuid4()) for _ in range(7)]

WALLET_SAMPLES = [
    Wallet(
        id=WALLET_IDS[0],
        name="User A Wallet",
        context={"user_id": "user_a", "type": "personal"},
        created_at=ONE_YEAR_AGO,
        updated_at=ONE_YEAR_AGO,
    ),
    Wallet(
        id=WALLET_IDS[1],
        name="User B Wallet",
        context={"user_id": "user_b", "type": "business"},
        created_at=ONE_YEAR_AGO,
        updated_at=ONE_YEAR_AGO,
    ),
    Wallet(
        id=WALLET_IDS[2],
        name="User C Wallet",
        context={"user_id": "user_c", "type": "personal"},
        created_at=ONE_YEAR_AGO,
        updated_at=ONE_YEAR_AGO,
    ),
    Wallet(
        id=WALLET_IDS[3],
        name="User D Wallet",
        context={"user_id": "user_d", "type": "business"},
        created_at=ONE_YEAR_AGO,
        updated_at=ONE_YEAR_AGO,
    ),
    Wallet(
        id=WALLET_IDS[4],
        name="User E Wallet",
        context={"user_id": "user_e", "type": "personal"},
        created_at=ONE_YEAR_AGO,
        updated_at=ONE_YEAR_AGO,
    ),
    Wallet(
        id=WALLET_IDS[5],
        name="User F Wallet",
        context={"user_id": "user_f", "type": "business"},
        created_at=ONE_YEAR_AGO,
        updated_at=ONE_YEAR_AGO,
    ),
    Wallet(
        id=WALLET_IDS[6],
        name="User G Wallet",
        context={"user_id": "user_g", "type": "personal"},
        created_at=ONE_YEAR_AGO,
        updated_at=ONE_YEAR_AGO,
    ),
]


class TransactionGenerator:
    def __init__(self, wallet_id: str, credit_type_id: str):
        self.wallet_id = wallet_id
        self.credit_type_id = credit_type_id
        self.current_date = datetime.now(timezone.utc) - timedelta(days=365)
        self.available_balance = 0
        self.held_balance = 0
        self.active_holds: Dict[str, float] = {}
        self.transactions: List[TransactionDBModel] = []
        self.transaction_counter = 0

    def advance_time(self, min_days=1, max_days=30):
        days = random.randint(min_days, max_days)
        self.current_date += timedelta(days=days)
        return self.current_date

    def create_transaction(
        self,
        type: TransactionType,
        description: str,
        payload: TransactionRequestPayload,
        hold_status: Optional[HoldStatus] = None,
        _id: Optional[str] = None,
    ) -> TransactionDBModel:
        self.transaction_counter += 1
        return TransactionDBModel(
            id=_id
            or str(uuid.uuid4()),  # Generate unique ObjectId for each transaction
            type=type,
            wallet_id=self.wallet_id,
            credit_type_id=self.credit_type_id,
            description=description,
            idempotency_key=(
                f"seed_{self.wallet_id}_"
                f"{self.credit_type_id}_{self.transaction_counter}"
            ),
            issuer="seed_script",
            context={"source": "seed_data"},
            payload=payload.model_dump(),
            hold_status=hold_status,
            status=TransactionStatus.COMPLETED,
            created_at=self.current_date,
            updated_at=self.current_date,
        )

    def add_deposit(self, amount: float, description: str = "Deposit"):
        transaction = self.create_transaction(
            type=TransactionType.DEPOSIT,
            description=description,
            payload=DepositTransactionRequestPayload(amount=amount),
        )
        self.available_balance += amount
        self.transactions.append(transaction)

    def add_hold(self, amount: float, description: str = "Hold"):
        if self.available_balance < amount:
            return None

        transaction = self.create_transaction(
            type=TransactionType.HOLD,
            description=description,
            payload=HoldTransactionRequestPayload(amount=amount),
            hold_status=HoldStatus.HELD,
        )

        hold_id = transaction.id
        self.active_holds[str(hold_id)] = amount
        self.available_balance -= amount
        self.held_balance += amount
        self.transactions.append(transaction)
        return hold_id

    def add_release(self, hold_id: str, description: str = "Release"):
        if hold_id not in self.active_holds:
            return

        amount = self.active_holds[hold_id]
        transaction = self.create_transaction(
            type=TransactionType.RELEASE,
            description=description,
            payload=ReleaseTransactionRequestPayload(hold_transaction_id=hold_id),
        )

        del self.active_holds[hold_id]
        self.available_balance += amount
        self.held_balance -= amount
        self.transactions.append(transaction)

    def add_debit(
        self, amount: float, hold_id: Optional[str] = None, description: str = "Debit"
    ):
        if hold_id and hold_id in self.active_holds:
            held_amount = self.active_holds[hold_id]
            if amount > held_amount:
                return

            transaction = self.create_transaction(
                type=TransactionType.DEBIT,
                description=description,
                payload=DebitTransactionRequestPayload(
                    amount=amount, hold_transaction_id=hold_id
                ),
            )

            del self.active_holds[hold_id]
            self.held_balance -= held_amount
            self.transactions.append(transaction)

        elif self.available_balance >= amount:
            transaction = self.create_transaction(
                type=TransactionType.DEBIT,
                description=description,
                payload=DebitTransactionRequestPayload(amount=amount),
            )

            self.available_balance -= amount
            self.transactions.append(transaction)

    def generate_transactions(self) -> List[TransactionDBModel]:
        # Initial deposit
        self.add_deposit(10000, "Initial deposit")

        # Set start date to exactly one year ago
        start_date = (datetime.now(timezone.utc) - timedelta(days=365)).date()
        end_date = datetime.now(timezone.utc).date()
        current_day = start_date

        # Generate transactions for each day
        while current_day <= end_date:
            # Ensure at least one transaction per day
            transaction_count = random.randint(1, 3)  # 1-3 transactions per day

            for _ in range(transaction_count):
                # Random deposit (30% chance)
                if random.random() < 0.3:
                    amount = round(random.uniform(100, 1000), 2)
                    self.add_deposit(amount, "Regular deposit")

                # Create hold (40% chance)
                if random.random() < 0.4:
                    hold_amount = round(random.uniform(50, 200), 2)
                    hold_id = self.add_hold(hold_amount, "Service hold")

                    if hold_id:
                        # Either use the hold or release it after a short delay
                        if random.random() < 0.7:
                            self.add_debit(hold_amount, str(hold_id), "Service charge")
                        else:
                            hold_transaction = next(
                                t
                                for t in self.transactions
                                if str(t.id) == str(hold_id)
                            )
                            self.add_release(str(hold_id), "Hold release")
                            hold_transaction.hold_status = HoldStatus.RELEASED

                # Direct debit (30% chance)
                if random.random() < 0.3:
                    debit_amount = round(random.uniform(10, 100), 2)
                    self.add_debit(debit_amount, description="Direct purchase")

            # Advance to next day
            self.current_date = datetime.combine(
                current_day + timedelta(days=1),
                self.current_date.time(),
                tzinfo=timezone.utc,
            )
            current_day = self.current_date.date()

        return self.transactions


def generate_seed_data() -> SeedData:
    """Generate all seed data in the correct structure."""
    seed_data = SeedData(
        credit_types=[ct for ct in CREDIT_TYPE_SAMPLES],
        wallets=[wallet for wallet in WALLET_SAMPLES],
        transactions=[],
    )
    print("Generating transactions...")
    for wallet in WALLET_SAMPLES:
        for credit_type in CREDIT_TYPE_SAMPLES:
            generator = TransactionGenerator(str(wallet.id), str(credit_type.id))
            seed_data.transactions.extend(generator.generate_transactions())
        print(f"Generated {len(seed_data.transactions)} transactions")

    return seed_data


if __name__ == "__main__":
    seed_data = generate_seed_data()
    print(f"Generated {len(seed_data.credit_types)} credit types")
    print(f"Generated {len(seed_data.wallets)} wallets")
    print(f"Generated {len(seed_data.transactions)} transactions")
