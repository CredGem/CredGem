import pytest
from decimal import Decimal
from datetime import datetime

from credgem import CredGemClient
from credgem.exceptions import InsufficientCreditsError


@pytest.fixture
async def client():
    """Create a client connected to the local API."""
    async with CredGemClient(
        api_key="test_key",
        base_url="http://localhost:8000/api"
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
        description="Test wallet",
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
    initial_balance = Decimal("1000.00")
    hold_amount = Decimal("10.00")
    
    async with client.draw_credits(
        wallet_id=funded_wallet.id,
        credit_type_id=credit_type.id,
        amount=hold_amount,
        description="Test transaction",
        issuer="test_system",
        transaction_id=transaction_id,
        context={"test": "value"}
    ) as draw:
        # Verify funds are held
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
        assert balance.held == hold_amount
        assert balance.available == initial_balance - hold_amount
        assert balance.spent == Decimal("0.00")
        
        # Perform debit
        await draw.debit()
        
        # Verify funds were debited
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
        assert balance.held == Decimal("0.00")
        assert balance.available == initial_balance - hold_amount
        assert balance.spent == hold_amount


@pytest.mark.asyncio
async def test_success_flow_skip_hold(client, funded_wallet, credit_type):
    """Test successful flow with skip_hold=True."""
    initial_balance = Decimal("1000.00")
    debit_amount = Decimal("10.00")
    
    async with client.draw_credits(
        wallet_id=funded_wallet.id,
        credit_type_id=credit_type.id,
        amount=debit_amount,
        description="Test direct debit",
        issuer="test_system",
        skip_hold=True
    ) as draw:
        # Verify no funds are held
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
        assert balance.held == Decimal("0.00")
        assert balance.available == initial_balance
        
        # Perform direct debit
        await draw.debit()
        
        # Verify funds were debited
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
        assert balance.held == Decimal("0.00")
        assert balance.available == initial_balance - debit_amount


@pytest.mark.asyncio
async def test_exception_auto_release(client, funded_wallet, credit_type):
    """Test automatic release on exception in context body."""
    hold_amount = Decimal("10.00")
    
    with pytest.raises(ValueError):
        async with client.draw_credits(
            wallet_id=funded_wallet.id,
            credit_type_id=credit_type.id,
            amount=hold_amount,
            description="Test exception",
            issuer="test_system"
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
    assert balance.held == Decimal("0.00")
    assert balance.available == Decimal("1000.00")


@pytest.mark.asyncio
async def test_no_debit_auto_release(client, funded_wallet, credit_type):
    """Test automatic release when debit is not called."""
    hold_amount = Decimal("10.00")
    
    async with client.draw_credits(
        wallet_id=funded_wallet.id,
        credit_type_id=credit_type.id,
        amount=hold_amount,
        description="Test no debit",
        issuer="test_system"
    ):
        # Verify funds are held
        wallet_info = await client.wallets.get(funded_wallet.id)
        balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
        assert balance.held == hold_amount
    
    # Verify funds were released
    wallet_info = await client.wallets.get(funded_wallet.id)
    balance = next(b for b in wallet_info.balances if b.credit_type_id == credit_type.id)
    assert balance.held == Decimal("0.00")
    assert balance.available == Decimal("1000.00")


# @pytest.mark.asyncio
# async def test_insufficient_credits(client, wallet, credit_type):
#     """Test handling of insufficient credits."""
#     # Try to hold more than available
#     with pytest.raises(InsufficientCreditsError):
#         async with client.draw_credits(
#             wallet_id=wallet.id,
#             credit_type_id=credit_type.id,
#             amount=Decimal("100000.00"),  # No funds in wallet
#             description="Test insufficient",
#             issuer="test_system"
#         ):
#             pass  # Should raise before reaching here


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