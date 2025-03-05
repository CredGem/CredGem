from datetime import datetime

import httpx
import pytest

from credgem import CredGemClient
from credgem.models.credit_types import CreditTypeRequest
from credgem.models.transactions import (
    DebitRequest,
    DepositRequest,
    HoldRequest,
    ReleaseRequest,
)
from credgem.models.wallets import WalletRequest


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
        CreditTypeRequest(
            name=f"TEST_POINTS_{datetime.now().timestamp()}",
            description="Test credit type",
        )
    )
    return credit_type


@pytest.fixture
async def wallet(client):
    """Create a test wallet."""
    wallet = await client.wallets.create(
        WalletRequest(
            name=f"Test Wallet {datetime.now().timestamp()}", context={"test": True}
        )
    )
    return wallet


@pytest.fixture
async def funded_wallet(client, wallet, credit_type):
    """Create a wallet with initial funds."""
    await client.transactions.deposit(
        DepositRequest(
            wallet_id=wallet.id,
            amount=1000,
            credit_type_id=credit_type.id,
            description="Initial test deposit",
            issuer="test_system",
        )
    )
    return wallet


@pytest.mark.asyncio
async def test_deposit_success(client, wallet, credit_type):
    """Test successful deposit transaction."""
    amount = 100

    # Perform deposit
    response = await client.transactions.deposit(
        DepositRequest(
            wallet_id=wallet.id,
            amount=amount,
            credit_type_id=credit_type.id,
            description="Test deposit",
            issuer="test_system",
        )
    )

    # Verify deposit was successful
    assert response.id is not None
    assert response.credit_type_id == credit_type.id

    # Verify wallet balance
    wallet_info = await client.wallets.get(wallet.id)
    balance = next(
        b for b in wallet_info.balances if b.credit_type_id == credit_type.id
    )
    assert balance.available == amount
    assert balance.held == 0
    assert balance.spent == 0


@pytest.mark.asyncio
async def test_deposit_with_transaction_id(client, wallet, credit_type):
    """Test deposit with specific transaction ID."""

    response = await client.transactions.deposit(
        DepositRequest(
            wallet_id=wallet.id,
            amount=50,
            credit_type_id=credit_type.id,
            description="Test deposit with transaction ID",
            issuer="test_system",
        )
    )

    # Verify deposit was successful
    assert response.id is not None
    assert response.credit_type_id == credit_type.id

    # Verify wallet balance
    wallet_info = await client.wallets.get(wallet.id)
    balance = next(
        b for b in wallet_info.balances if b.credit_type_id == credit_type.id
    )
    assert balance.available == 50


@pytest.mark.asyncio
async def test_debit_success(client, funded_wallet, credit_type):
    """Test successful debit transaction."""
    debit_amount = 30
    response = await client.transactions.debit(
        DebitRequest(
            wallet_id=funded_wallet.id,
            amount=debit_amount,
            credit_type_id=credit_type.id,
            description="Test debit",
            issuer="test_system",
        )
    )

    # Verify debit was successful
    assert response.id is not None
    assert response.credit_type_id == credit_type.id

    # Verify wallet balance
    wallet_info = await client.wallets.get(funded_wallet.id)
    balance = next(
        b for b in wallet_info.balances if b.credit_type_id == credit_type.id
    )
    assert balance.available == 970
    assert balance.held == 0
    assert balance.spent == debit_amount


@pytest.mark.asyncio
async def test_debit_insufficient_funds(client, funded_wallet, credit_type):
    """Test debit with insufficient funds."""
    try:
        await client.transactions.debit(
            DebitRequest(
                wallet_id=funded_wallet.id,
                amount=200000,
                credit_type_id=credit_type.id,
                description="Test debit",
                issuer="test_system",
            )
        )
        pytest.fail("Expected insufficient balance error")
    except httpx.HTTPStatusError as e:
        assert e.response.status_code == 402
        assert "Insufficient balance" in str(e.response.json()["detail"])


@pytest.mark.asyncio
async def test_hold_and_release(client, funded_wallet, credit_type):
    """Test hold creation and release."""
    hold_amount = 30

    # Create hold
    hold = await client.transactions.hold(
        DebitRequest(
            wallet_id=funded_wallet.id,
            amount=hold_amount,
            credit_type_id=credit_type.id,
            description="Test hold",
            issuer="test_system",
        )
    )

    # Verify hold was created
    wallet_info = await client.wallets.get(funded_wallet.id)
    balance = next(
        b for b in wallet_info.balances if b.credit_type_id == credit_type.id
    )
    assert balance.held == hold_amount
    assert balance.available == 970

    # Release hold
    await client.transactions.release(
        ReleaseRequest(
            wallet_id=funded_wallet.id,
            hold_transaction_id=hold.id,
            credit_type_id=credit_type.id,
            description="Test release",
            issuer="test_system",
        )
    )

    # Verify hold was released
    wallet_info = await client.wallets.get(funded_wallet.id)
    balance = next(
        b for b in wallet_info.balances if b.credit_type_id == credit_type.id
    )
    assert balance.held == 0
    assert balance.available == 1000


@pytest.mark.asyncio
async def test_hold_and_debit(client, funded_wallet, credit_type):
    """Test hold creation followed by debit."""
    hold_amount = 30
    initial_balance = 1000

    # Create hold
    hold = await client.transactions.hold(
        HoldRequest(
            wallet_id=funded_wallet.id,
            amount=hold_amount,
            credit_type_id=credit_type.id,
            description="Test hold",
            issuer="test_system",
        )
    )

    # Verify hold was created
    wallet_info = await client.wallets.get(funded_wallet.id)
    balance = next(
        b for b in wallet_info.balances if b.credit_type_id == credit_type.id
    )
    assert balance.held == hold_amount
    assert balance.available == initial_balance - hold_amount

    # Debit using hold
    await client.transactions.debit(
        DebitRequest(
            wallet_id=funded_wallet.id,
            amount=hold_amount,
            credit_type_id=credit_type.id,
            description="Test debit with hold",
            issuer="test_system",
            hold_transaction_id=hold.id,
        )
    )

    # Verify final state
    wallet_info = await client.wallets.get(funded_wallet.id)
    balance = next(
        b for b in wallet_info.balances if b.credit_type_id == credit_type.id
    )
    assert balance.held == 0
    assert balance.available == initial_balance - hold_amount
    assert balance.spent == hold_amount


@pytest.mark.asyncio
async def test_hold_insufficient_funds(client, funded_wallet, credit_type):
    """Test hold with insufficient funds."""
    try:
        await client.transactions.hold(
            HoldRequest(
                wallet_id=funded_wallet.id,
                amount=2000,
                credit_type_id=credit_type.id,
                description="Test hold",
                issuer="test_system",
            )
        )
        pytest.fail("Expected insufficient balance error")
    except httpx.HTTPStatusError as e:
        assert e.response.status_code == 402
        assert "Insufficient balance" in str(e.response.json()["detail"])


@pytest.mark.asyncio
async def test_debit_with_invalid_hold(client, funded_wallet, credit_type):
    """Test debit with invalid hold transaction ID."""
    with pytest.raises(Exception):  # Specific exception type depends on API
        await client.transactions.debit(
            DebitRequest(
                wallet_id=funded_wallet.id,
                amount=30.00,
                credit_type_id=credit_type.id,
                description="Test debit",
                issuer="test_system",
                hold_transaction_id="invalid_hold_id",
            )
        )


@pytest.mark.asyncio
async def test_multiple_holds(client, funded_wallet, credit_type):
    """Test multiple holds on the same wallet."""
    # Create first hold
    hold1_amount = 30
    hold1 = await client.transactions.hold(
        HoldRequest(
            wallet_id=funded_wallet.id,
            amount=hold1_amount,
            credit_type_id=credit_type.id,
            description="Test hold 1",
            issuer="test_system",
        )
    )

    # Create second hold
    hold2_amount = 50
    hold2 = await client.transactions.hold(
        HoldRequest(
            wallet_id=funded_wallet.id,
            amount=hold2_amount,
            credit_type_id=credit_type.id,
            description="Test hold 2",
            issuer="test_system",
        )
    )

    # Verify both holds are active
    wallet_info = await client.wallets.get(funded_wallet.id)
    balance = next(
        b for b in wallet_info.balances if b.credit_type_id == credit_type.id
    )
    assert balance.held == hold1_amount + hold2_amount
    assert balance.available == 920

    # Release both holds
    await client.transactions.release(
        ReleaseRequest(
            wallet_id=funded_wallet.id,
            hold_transaction_id=hold1.id,
            credit_type_id=credit_type.id,
            description="Release hold 1",
            issuer="test_system",
        )
    )

    await client.transactions.release(
        ReleaseRequest(
            wallet_id=funded_wallet.id,
            hold_transaction_id=hold2.id,
            credit_type_id=credit_type.id,
            description="Release hold 2",
            issuer="test_system",
        )
    )

    # Verify all holds are released
    wallet_info = await client.wallets.get(funded_wallet.id)
    balance = next(
        b for b in wallet_info.balances if b.credit_type_id == credit_type.id
    )
    assert balance.held == 0
    assert balance.available == 1000
