from datetime import datetime

import pytest

from credgem import CredGemClient


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


@pytest.mark.asyncio
async def test_create_wallet(client):
    """Test wallet creation with basic properties."""
    name = f"Test Wallet {datetime.now().timestamp()}"
    context = {"test": True}

    wallet = await client.wallets.create(name=name, context=context)

    assert wallet.id is not None
    assert wallet.name == name
    assert wallet.context == context
    assert wallet.balances == []


@pytest.mark.asyncio
async def test_create_wallet_minimal(client):
    """Test wallet creation with minimal properties."""
    name = f"Test Wallet {datetime.now().timestamp()}"

    wallet = await client.wallets.create(name=name)

    assert wallet.id is not None
    assert wallet.name == name
    assert wallet.context == {}
    assert wallet.balances == []


@pytest.mark.asyncio
async def test_get_wallet(client):
    """Test retrieving a wallet by ID."""
    # Create a wallet first
    name = f"Test Wallet {datetime.now().timestamp()}"
    created_wallet = await client.wallets.create(name=name)

    # Retrieve the wallet
    wallet = await client.wallets.get(created_wallet.id)

    assert wallet.id == created_wallet.id
    assert wallet.name == name
    assert wallet.balances == []


@pytest.mark.asyncio
async def test_update_wallet(client):
    """Test updating wallet properties."""
    # Create a wallet first
    original_name = f"Test Wallet {datetime.now().timestamp()}"
    wallet = await client.wallets.create(name=original_name)

    # Update the wallet
    new_name = f"Updated Wallet {datetime.now().timestamp()}"
    new_context = {"updated": True}

    updated_wallet = await client.wallets.update(
        wallet_id=wallet.id, name=new_name, context=new_context
    )

    assert updated_wallet.id == wallet.id
    assert updated_wallet.name == new_name
    assert updated_wallet.context == new_context


@pytest.mark.asyncio
async def test_partial_update_wallet(client):
    """Test partial update of wallet properties."""
    # Create a wallet first
    original_name = f"Test Wallet {datetime.now().timestamp()}"
    original_context = {"original": True}

    wallet = await client.wallets.create(name=original_name, context=original_context)

    # Update only the name
    new_name = f"Updated Wallet {datetime.now().timestamp()}"
    updated_wallet = await client.wallets.update(wallet_id=wallet.id, name=new_name)

    assert updated_wallet.id == wallet.id
    assert updated_wallet.name == new_name
    assert updated_wallet.context == original_context


@pytest.mark.asyncio
async def test_list_wallets(client):
    """Test listing wallets with pagination."""
    # Create some wallets
    wallet_names = []
    for i in range(3):
        name = f"Test Wallet {i} {datetime.now().timestamp()}"
        await client.wallets.create(name=name)
        wallet_names.append(name)

    # List wallets with pagination
    response = await client.wallets.list(page=1, page_size=2)

    assert len(response.data) == 2
    assert response.page == 1
    assert response.page_size == 2
    assert response.total_count > 0


@pytest.mark.asyncio
async def test_wallet_with_balance(client, credit_type):
    """Test wallet creation and balance management."""
    # Create a wallet
    wallet = await client.wallets.create(
        name=f"Test Wallet {datetime.now().timestamp()}"
    )

    # Deposit credits
    deposit_amount = 100
    await client.transactions.deposit(
        wallet_id=wallet.id,
        amount=deposit_amount,
        credit_type_id=credit_type.id,
        description="Test deposit",
        issuer="test_system",
    )

    # Get updated wallet info
    updated_wallet = await client.wallets.get(wallet.id)
    balance = next(
        b for b in updated_wallet.balances if b.credit_type_id == credit_type.id
    )

    assert balance.available == deposit_amount
    assert balance.held == 0
    assert balance.spent == 0


@pytest.mark.asyncio
async def test_wallet_with_multiple_credit_types(client):
    """Test wallet with multiple credit types."""
    # Create two credit types
    credit_type1 = await client.credit_types.create(
        name=f"TEST_POINTS_1_{datetime.now().timestamp()}",
        description="Test credit type 1",
    )
    credit_type2 = await client.credit_types.create(
        name=f"TEST_POINTS_2_{datetime.now().timestamp()}",
        description="Test credit type 2",
    )

    # Create a wallet
    wallet = await client.wallets.create(
        name=f"Test Wallet {datetime.now().timestamp()}"
    )

    # Deposit different credit types
    await client.transactions.deposit(
        wallet_id=wallet.id,
        amount=100,
        credit_type_id=credit_type1.id,
        description="Test deposit 1",
        issuer="test_system",
    )

    await client.transactions.deposit(
        wallet_id=wallet.id,
        amount=200,
        credit_type_id=credit_type2.id,
        description="Test deposit 2",
        issuer="test_system",
    )

    # Get updated wallet info
    updated_wallet = await client.wallets.get(wallet.id)

    # Verify balances for both credit types
    balance1 = next(
        b for b in updated_wallet.balances if b.credit_type_id == credit_type1.id
    )
    balance2 = next(
        b for b in updated_wallet.balances if b.credit_type_id == credit_type2.id
    )

    assert balance1.available == 100
    assert balance2.available == 200
