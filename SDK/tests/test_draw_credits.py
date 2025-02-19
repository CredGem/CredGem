import pytest
from decimal import Decimal
from datetime import datetime

from credgem import CredGemClient
from credgem.exceptions import InsufficientCreditsError


@pytest.fixture
async def client():
    """Create a client connected to the local API."""
    async with CredGemClient(
        api_key="test_key", base_url="http://localhost:8000/api/v1"
    ) as client:
        yield client


@pytest.fixture
async def credit_type(client):
    """Create a test credit type."""
    credit_type = await client.credit_types.create(
        name=f"TEST_POINTS_{datetime.now().timestamp()}", description="Test credit type"
    )
    return credit_type


@pytest.fixture
async def wallet(client):
    """Create a test wallet."""
    wallet = await client.wallets.create(
        name=f"Test Wallet {datetime.now().timestamp()}", context={"test": True}
    )
    return wallet


@pytest.fixture
async def funded_wallet(client, wallet, credit_type):
    """Create a wallet with initial funds."""
    # Add initial funds
    await client.transactions.deposit(
        wallet_id=wallet.id,
        amount=Decimal("1000.00"),
        credit_type_id=credit_type.id,
        description="Initial test deposit",
        issuer="test_system",
    )
    return wallet


@pytest.mark.asyncio
async def test_success_flow_with_hold(client, funded_wallet, credit_type):
    """Test successful flow with hold and debit."""
    transaction_id = f"test_tx_{datetime.now().timestamp()}"
    initial_balance = 1000
    hold_amount = 10

    async with client.draw_credits(
        wallet_id=funded_wallet.id,
        credit_type_id=credit_type.id,
        amount=hold_amount,
        description="Test transaction",
        issuer="test_system",
        external_transaction_id=transaction_id,
        context={"test": "value"},
    ) as draw:
        # Verify funds are held
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(
            b for b in wallet_info.balances if b.credit_type_id == credit_type.id
        )
        assert balance.held == hold_amount
        assert balance.available == initial_balance - hold_amount
        assert balance.spent == 0

        # Perform debit
        await draw.debit()

        # Verify funds were debited
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(
            b for b in wallet_info.balances if b.credit_type_id == credit_type.id
        )
        assert balance.held == 0
        assert balance.available == initial_balance - hold_amount
        assert balance.spent == hold_amount


@pytest.mark.asyncio
async def test_success_flow_skip_hold(client, funded_wallet, credit_type):
    """Test successful flow with skip_hold=True."""
    initial_balance = 1000
    debit_amount = 10.00
    external_transaction_id = f"test_tx_{datetime.now().timestamp()}"
    async with client.draw_credits(
        wallet_id=funded_wallet.id,
        credit_type_id=credit_type.id,
        amount=debit_amount,
        description="Test direct debit",
        issuer="test_system",
        external_transaction_id=external_transaction_id,
        skip_hold=True,
    ) as draw:
        # Verify no funds are held
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(
            b for b in wallet_info.balances if b.credit_type_id == credit_type.id
        )
        assert balance.held == 0
        assert balance.available == initial_balance

        # Perform direct debit
        await draw.debit()

        # Verify funds were debited
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(
            b for b in wallet_info.balances if b.credit_type_id == credit_type.id
        )
        assert balance.held == 0
        assert balance.available == initial_balance - debit_amount


@pytest.mark.asyncio
async def test_exception_auto_release(client, funded_wallet, credit_type):
    """Test automatic release on exception in context body."""
    hold_amount = 10
    external_transaction_id = f"test_tx_{datetime.now().timestamp()}"
    with pytest.raises(ValueError):
        async with client.draw_credits(
            wallet_id=funded_wallet.id,
            credit_type_id=credit_type.id,
            amount=hold_amount,
            description="Test exception",
            issuer="test_system",
            external_transaction_id=external_transaction_id,
        ):
            # Verify funds are held
            wallet_info = await client.wallets.get(funded_wallet.id)
            balance = next(
                b for b in wallet_info.balances if b.credit_type_id == credit_type.id
            )
            assert balance.held == hold_amount

            # Raise exception
            raise ValueError("Test error")

    # Verify funds were released
    wallet_info = await client.wallets.get(funded_wallet.id)
    balance = next(
        b for b in wallet_info.balances if b.credit_type_id == credit_type.id
    )
    assert balance.held == 0
    assert balance.available == 1000
