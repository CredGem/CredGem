import pytest
from decimal import Decimal
from datetime import datetime

from httpx import HTTPStatusError

from credgem import CredGemClient
from credgem.exceptions import InsufficientCreditsError


@pytest.fixture
async def client():
    """Create a client connected to the local API."""
    async with CredGemClient(
        api_key="test_key",
        base_url="http://localhost:8000/api/v1"
    ) as client:
        yield client


@pytest.fixture
async def credit_type(client):
    """Create a test credit type."""
    credit_type = await client.credit_types.create(
        name=f"TEST_POINTS_{datetime.now().timestamp()}",
        description="Test credit type"
    )
    return credit_type


@pytest.fixture
async def wallet(client):
    """Create a test wallet."""
    wallet = await client.wallets.create(
        name=f"Test Wallet {datetime.now().timestamp()}",
        context={"test": True}
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
        issuer="test_system"
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
        context={"test": "value"}
    ) as draw:
        # Verify funds are held
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
        assert balance.held == hold_amount
        assert balance.available == initial_balance - hold_amount
        assert balance.spent == 0
        
        # Perform debit
        await draw.debit()
        
        # Verify funds were debited
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
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
        skip_hold=True
    ) as draw:
        # Verify no funds are held
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
        assert balance.held == 0
        assert balance.available == initial_balance
        
        # Perform direct debit
        await draw.debit()
        
        # Verify funds were debited
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
        assert balance.held == 0
        assert balance.available == initial_balance - debit_amount


@pytest.mark.asyncio
async def test_exception_auto_release(client, funded_wallet, credit_type):
    """Test automatic release on exception in context body."""
    hold_amount = 10
    external_transaction_id=f"test_tx_{datetime.now().timestamp()}"
    with pytest.raises(ValueError):
        async with client.draw_credits(
            wallet_id=funded_wallet.id,
            credit_type_id=credit_type.id,
            amount=hold_amount,
            description="Test exception",
            issuer="test_system",
            external_transaction_id=external_transaction_id
        ):
            # Verify funds are held
            wallet_info = await client.wallets.get(funded_wallet.id)
            balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
            assert balance.held == hold_amount
            
            # Raise exception
            raise ValueError("Test error")
    
    # Verify funds were released
    wallet_info = await client.wallets.get(funded_wallet.id)
    balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
    assert balance.held == 0
    assert balance.available == 1000


@pytest.mark.asyncio
async def test_insufficient_credits(client, funded_wallet, credit_type):
    """Test handling of insufficient credits."""
    # Try to hold more than available
    with pytest.raises(HTTPStatusError) as exc_info:
        async with client.draw_credits(
            wallet_id=funded_wallet.id,
            credit_type_id=credit_type.id,
            amount=1000000,  # No funds in wallet
            description="Test insufficient",
            issuer="test_system"
        ):
            pass  # Should raise before reaching here
    assert exc_info.value.response.status_code ==402

# @pytest.mark.asyncio
# async def test_idempotency(client, funded_wallet, credit_type):
#     """Test idempotency with same transaction ID."""
#     amount = Decimal("10.00")
#     transaction_id = "test_tx_123"
    
#     # First attempt
#     async with client.draw_credits(
#         wallet_id=funded_wallet.id,
#         credit_type_id=credit_type.id,
#         amount=amount,
#         description="Test idempotency",
#         issuer="test_system",
#         transaction_id=transaction_id
#     ) as draw:
#         await draw.debit()
    
#     initial_balance = await client.wallets.get(funded_wallet.id)
    
#     # Second attempt with same transaction ID
#     async with client.draw_credits(
#         wallet_id=funded_wallet.id,
#         credit_type_id=credit_type.id,
#         amount=amount,
#         description="Test idempotency",
#         issuer="test_system",
#         transaction_id=transaction_id
#     ) as draw:
#         await draw.debit()
    
#     # Verify balance hasn't changed after second attempt
#     final_balance = await client.wallets.get(funded_wallet.id)
#     assert initial_balance == final_balance 


@pytest.mark.asyncio
async def test_model_optional_fields(client, credit_type):
    """Test that models handle optional fields correctly."""
    # Test wallet creation with minimal fields
    wallet = await client.wallets.create(
        name=f"Test Wallet {datetime.now().timestamp()}"
    )
    assert wallet.context == {}  # Should use default empty dict
    assert wallet.description is None  # Optional field should be None
    assert isinstance(wallet.balances, list)  # Should be empty list
    assert len(wallet.balances) == 0

    # Test wallet with all fields
    wallet_with_context = await client.wallets.create(
        name=f"Test Wallet {datetime.now().timestamp()}",
        description="Test description",
        context={"test": True}
    )
    assert wallet_with_context.description == "Test description"
    assert wallet_with_context.context == {"test": True}


@pytest.mark.asyncio
async def test_model_extra_fields(client, credit_type):
    """Test that models handle extra fields from server gracefully."""
    wallet = await client.wallets.create(
        name=f"Test Wallet {datetime.now().timestamp()}"
    )
    
    # Verify the model works even with standard fields
    assert wallet.id
    assert wallet.name
    assert wallet.created_at
    assert wallet.updated_at

    # Add funds to test Balance model
    await client.transactions.deposit(
        wallet_id=wallet.id,
        amount=Decimal("100.00"),
        credit_type_id=credit_type.id,
        description="Test deposit",
        issuer="test_system"
    )

    # Get wallet info and verify Balance objects work
    wallet_info = await client.wallets.get(wallet.id)
    balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
    assert balance.available == 100.0
    assert balance.held == 0.0
    assert balance.spent == 0.0


@pytest.mark.asyncio
async def test_reuse_existing_hold(client, funded_wallet, credit_type):
    """Test reusing an existing hold with the same external transaction ID."""
    initial_balance = 1000
    hold_amount = 10
    external_transaction_id = f"test_tx_{datetime.now().timestamp()}"

    # First attempt - create hold without debit
    async with client.draw_credits(
        wallet_id=funded_wallet.id,
        credit_type_id=credit_type.id,
        amount=hold_amount,
        description="Test hold reuse",
        issuer="test_system",
        external_transaction_id=external_transaction_id,
    ) as draw:
        # Verify funds are held
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
        assert balance.held == hold_amount
        assert balance.available == initial_balance - hold_amount
        # Exit without debiting

    # Second attempt - should reuse existing hold and complete debit
    async with client.draw_credits(
        wallet_id=funded_wallet.id,
        credit_type_id=credit_type.id,
        amount=hold_amount,
        description="Test hold reuse",
        issuer="test_system",
        external_transaction_id=external_transaction_id
    ) as draw:
        # Verify the hold is still active
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
        assert balance.held == hold_amount
        assert balance.available == initial_balance - hold_amount

        # Now complete the debit
        await draw.debit()

        # Verify funds were debited
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
        assert balance.held == 0
        assert balance.available == initial_balance - hold_amount
        assert balance.spent == hold_amount 