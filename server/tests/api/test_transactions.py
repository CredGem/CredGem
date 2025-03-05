from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from src.core.settings import settings
from src.models.transactions import (
    AdjustTransactionRequest,
    AdjustTransactionRequestPayload,
    DebitTransactionRequest,
    DebitTransactionRequestPayload,
    DepositTransactionRequest,
    DepositTransactionRequestPayload,
    HoldStatus,
    HoldTransactionRequest,
    HoldTransactionRequestPayload,
    ReleaseTransactionRequest,
    ReleaseTransactionRequestPayload,
)
from src.models.wallets import CreateWalletRequest
from src.utils.constants import (
    BALANCE_NOT_FOUND_ERROR,
    DUPLICATE_TRANSACTION_ERROR,
    HOLD_AMOUNT_EXCEEDS_ERROR,
    HOLD_TRANSACTION_NOT_FOUND_ERROR,
    HOLD_TRANSACTION_NOT_HELD_ERROR,
    INSUFFICIENT_BALANCE_ERROR,
)

pytestmark = pytest.mark.anyio


class TestTransactions:
    base_url = settings.API_V1_STR

    async def setup_wallet_and_credit_type(self, client: AsyncClient):
        user_id = str(uuid4())
        # Create a wallet
        wallet_request = CreateWalletRequest(
            name="test_transaction_wallet", context={"user_id": user_id}
        )
        wallet_response = await client.post(
            f"{self.base_url}/wallets/", json=wallet_request.model_dump()
        )
        wallet_id = wallet_response.json()["id"]

        # Create a credit type
        credit_type_request = {
            "name": "test_transaction_credit_type",
            "description": "Test credit type for transaction tests",
        }
        credit_type_response = await client.post(
            f"{self.base_url}/credit-types", json=credit_type_request
        )
        credit_type_id = credit_type_response.json()["id"]

        return wallet_id, credit_type_id

    def find_balance(self, balances: list[dict], credit_type_id: str) -> dict | None:
        for balance in balances:
            if balance["credit_type_id"] == credit_type_id:
                return balance
        return None

    async def test_deposit_transaction(self, client: AsyncClient):
        issuer = "test_user"
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)

        # Create a credit transaction
        transaction_request = DepositTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test credit transaction",
            payload=DepositTransactionRequestPayload(amount=100),
            issuer=issuer,
        )

        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=transaction_request.model_dump(),
        )
        assert response.status_code == status.HTTP_200_OK
        # Check the wallet balance

        wallet_response = await client.get(f"{self.base_url}/wallets/{wallet_id}")
        assert wallet_response.status_code == status.HTTP_200_OK
        wallet_data = wallet_response.json()
        balance = self.find_balance(wallet_data["balances"], credit_type_id)
        assert balance is not None
        assert balance.get("available") == 100
        assert balance.get("spent") == 0
        assert balance.get("held") == 0

    async def test_debit_nonexistent_balance(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)

        debit_request = DebitTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test debit transaction",
            payload=DebitTransactionRequestPayload(amount=100),
            issuer="test_user",
        )

        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/debit",
            json=debit_request.model_dump(),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == BALANCE_NOT_FOUND_ERROR

    async def test_debit_transaction(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)

        # First credit the wallet
        credit_request = DepositTransactionRequest(
            credit_type_id=credit_type_id,
            description="Initial credit",
            payload=DepositTransactionRequestPayload(amount=100),
            issuer="test_user",
        )
        await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=credit_request.model_dump(),
        )

        # Create a debit transaction
        debit_request = DebitTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test debit transaction",
            payload=DebitTransactionRequestPayload(amount=50),
            issuer="test_user",
        )

        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/debit",
            json=debit_request.model_dump(),
        )
        assert response.status_code == status.HTTP_200_OK

        # Check the wallet balance
        wallet_response = await client.get(f"{self.base_url}/wallets/{wallet_id}")
        assert wallet_response.status_code == status.HTTP_200_OK
        wallet_data = wallet_response.json()
        balance = self.find_balance(wallet_data["balances"], credit_type_id)
        assert balance is not None
        assert balance.get("available") == 50
        assert balance.get("spent") == 50
        assert balance.get("held") == 0
        assert balance.get("overall_spent") == 50

    async def test_insufficient_balance_debit(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)

        # First credit a small amount
        credit_request = DepositTransactionRequest(
            credit_type_id=credit_type_id,
            description="Small initial credit",
            payload=DepositTransactionRequestPayload(amount=20),
            issuer="test_user",
        )
        await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=credit_request.model_dump(),
        )

        # Try to debit without any balance
        debit_request = DebitTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test insufficient balance debit",
            payload=DebitTransactionRequestPayload(amount=50),
            issuer="test_user",
        )

        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/debit",
            json=debit_request.model_dump(),
        )
        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED
        data = response.json()
        assert data["detail"] == INSUFFICIENT_BALANCE_ERROR

    async def test_hold_nonexistent_balance(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)

        hold_request = HoldTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test hold transaction",
            payload=HoldTransactionRequestPayload(amount=100),
            issuer="test_user",
        )
        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/hold",
            json=hold_request.model_dump(),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == BALANCE_NOT_FOUND_ERROR

    async def test_hold_transaction(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)

        # First credit the wallet
        credit_request = DepositTransactionRequest(
            credit_type_id=credit_type_id,
            description="Initial credit",
            payload=DepositTransactionRequestPayload(amount=100),
            issuer="test_user",
        )
        await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=credit_request.model_dump(),
        )

        # Create a hold transaction
        hold_request = HoldTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test hold transaction",
            payload=HoldTransactionRequestPayload(amount=30),
            issuer="test_user",
        )

        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/hold", json=hold_request.model_dump()
        )
        assert response.status_code == status.HTTP_200_OK

        # Check the wallet balance
        wallet_response = await client.get(f"{self.base_url}/wallets/{wallet_id}")
        assert wallet_response.status_code == status.HTTP_200_OK
        wallet_data = wallet_response.json()
        balance = self.find_balance(wallet_data["balances"], credit_type_id)
        assert balance is not None
        assert balance.get("available") == 70
        assert balance.get("spent") == 0
        assert balance.get("held") == 30

    async def test_debit_with_hold(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)
        credit_request = DepositTransactionRequest(
            credit_type_id=credit_type_id,
            description="Initial credit",
            payload=DepositTransactionRequestPayload(amount=100),
            issuer="test_user",
        )
        await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=credit_request.model_dump(),
        )

        # Create a hold transaction
        hold_request = HoldTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test hold transaction",
            payload=HoldTransactionRequestPayload(amount=30),
            issuer="test_user",
        )
        hold_response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/hold",
            json=hold_request.model_dump(),
        )
        assert hold_response.status_code == status.HTTP_200_OK
        assert hold_response.json()["hold_status"] == HoldStatus.HELD.value
        hold_data = hold_response.json()

        # Create a debit transaction
        debit_request = DebitTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test debit transaction",
            payload=DebitTransactionRequestPayload(
                amount=20, hold_transaction_id=hold_data["id"]
            ),
            issuer="test_user",
        )

        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/debit",
            json=debit_request.model_dump(),
        )
        assert response.status_code == status.HTTP_200_OK

        hold_transaction_response = await client.get(
            f"{self.base_url}/transactions/{hold_data['id']}"
        )
        assert hold_transaction_response.status_code == status.HTTP_200_OK
        assert hold_transaction_response.json()["hold_status"] == HoldStatus.USED.value

        # Check the wallet balance
        wallet_response = await client.get(f"{self.base_url}/wallets/{wallet_id}")
        assert wallet_response.status_code == status.HTTP_200_OK
        wallet_data = wallet_response.json()
        balance = self.find_balance(wallet_data["balances"], credit_type_id)
        assert balance is not None
        assert balance.get("available") == 80
        assert balance.get("spent") == 20
        assert balance.get("held") == 0

    async def test_debit_with_hold_same_amount(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)
        credit_request = DepositTransactionRequest(
            credit_type_id=credit_type_id,
            description="Initial credit",
            payload=DepositTransactionRequestPayload(amount=100),
            issuer="test_user",
        )
        await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=credit_request.model_dump(),
        )
        hold_amount = 10

        # Create a hold transaction
        hold_request = HoldTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test hold transaction",
            payload=HoldTransactionRequestPayload(amount=hold_amount),
            issuer="test_user",
        )
        hold_response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/hold",
            json=hold_request.model_dump(),
        )
        assert hold_response.status_code == status.HTTP_200_OK
        hold_data = hold_response.json()

        # Create a debit transaction
        debit_request = DebitTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test debit transaction",
            payload=DebitTransactionRequestPayload(
                amount=hold_amount, hold_transaction_id=hold_data["id"]
            ),
            issuer="test_user",
        )
        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/debit",
            json=debit_request.model_dump(),
        )
        assert response.status_code == status.HTTP_200_OK

        wallet_response = await client.get(f"{self.base_url}/wallets/{wallet_id}")
        assert wallet_response.status_code == status.HTTP_200_OK
        wallet_data = wallet_response.json()
        balance = self.find_balance(wallet_data["balances"], credit_type_id)
        assert balance is not None
        assert balance.get("available") == 90
        assert balance.get("spent") == 10
        assert balance.get("held") == 0

    async def test_debit_with_hold_not_enough_held(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)

        # First credit the wallet
        credit_request = DepositTransactionRequest(
            credit_type_id=credit_type_id,
            description="Initial credit",
            payload=DepositTransactionRequestPayload(amount=100),
            issuer="test_user",
        )
        await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=credit_request.model_dump(),
        )

        # Create a hold transaction
        hold_request = HoldTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test hold transaction",
            payload=HoldTransactionRequestPayload(amount=30),
            issuer="test_user",
        )
        hold_response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/hold",
            json=hold_request.model_dump(),
        )
        assert hold_response.status_code == status.HTTP_200_OK
        hold_data = hold_response.json()

        # Create a debit transaction
        debit_request = DebitTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test debit transaction",
            payload=DebitTransactionRequestPayload(
                amount=50, hold_transaction_id=hold_data["id"]
            ),
            issuer="test_user",
        )

        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/debit",
            json=debit_request.model_dump(),
        )
        assert response.status_code == status.HTTP_402_PAYMENT_REQUIRED
        assert response.json()["detail"] == HOLD_AMOUNT_EXCEEDS_ERROR

    async def test_release_nonexistent_hold(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)
        release_request = ReleaseTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test release transaction",
            payload=ReleaseTransactionRequestPayload(hold_transaction_id=str(uuid4())),
            issuer="test_user",
        )
        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/release",
            json=release_request.model_dump(),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == HOLD_TRANSACTION_NOT_FOUND_ERROR

    async def test_release_transaction_not_held(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)
        # Initial deposit
        credit_request = DepositTransactionRequest(
            credit_type_id=credit_type_id,
            description="Initial credit",
            payload=DepositTransactionRequestPayload(amount=100),
            issuer="test_user",
        )
        await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=credit_request.model_dump(),
        )

        # Create a hold transaction
        hold_request = HoldTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test hold transaction",
            payload=HoldTransactionRequestPayload(amount=30),
            issuer="test_user",
        )
        hold_response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/hold",
            json=hold_request.model_dump(),
        )
        assert hold_response.status_code == status.HTTP_200_OK
        hold_data = hold_response.json()
        assert hold_data["hold_status"] == HoldStatus.HELD.value
        hold_id = hold_data["id"]

        # Release the hold
        release_request = ReleaseTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test release transaction",
            payload=ReleaseTransactionRequestPayload(hold_transaction_id=hold_id),
            issuer="test_user",
        )
        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/release",
            json=release_request.model_dump(),
        )
        assert response.status_code == status.HTTP_200_OK

        # Get the hold transaction and verify it's now released
        hold_response = await client.get(f"{self.base_url}/transactions/{hold_id}")
        assert hold_response.status_code == status.HTTP_200_OK
        updated_hold = hold_response.json()
        assert updated_hold["hold_status"] == HoldStatus.RELEASED.value

        release_request = ReleaseTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test release transaction",
            payload=ReleaseTransactionRequestPayload(hold_transaction_id=hold_id),
            issuer="test_user",
        )
        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/release",
            json=release_request.model_dump(),
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == HOLD_TRANSACTION_NOT_HELD_ERROR

    async def test_release_transaction(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)
        credit_request = DepositTransactionRequest(
            credit_type_id=credit_type_id,
            description="Initial credit",
            payload=DepositTransactionRequestPayload(amount=100),
            issuer="test_user",
        )
        await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=credit_request.model_dump(),
        )

        # Create a hold transaction
        hold_request = HoldTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test hold transaction",
            payload=HoldTransactionRequestPayload(amount=30),
            issuer="test_user",
        )
        hold_response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/hold", json=hold_request.model_dump()
        )
        hold_data = hold_response.json()

        # Create a release transaction
        release_request = ReleaseTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test release transaction",
            payload=ReleaseTransactionRequestPayload(
                hold_transaction_id=hold_data["id"]
            ),
            issuer="test_user",
        )

        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/release",
            json=release_request.model_dump(),
        )
        assert response.status_code == status.HTTP_200_OK

        # Check the wallet balance
        wallet_response = await client.get(f"{self.base_url}/wallets/{wallet_id}")
        assert wallet_response.status_code == status.HTTP_200_OK
        wallet_data = wallet_response.json()
        balance = self.find_balance(wallet_data["balances"], credit_type_id)
        assert balance is not None
        assert balance.get("available") == 100
        assert balance.get("spent") == 0
        assert balance.get("held") == 0

    async def test_invalid_release_transaction(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)

        invalid_hold_id = str(uuid4())

        # Try to release without a hold
        release_request = ReleaseTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test invalid release transaction",
            payload=ReleaseTransactionRequestPayload(
                hold_transaction_id=invalid_hold_id
            ),
            issuer="test_user",
        )

        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/release",
            json=release_request.model_dump(),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_adjust_nonexistent_balance(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)
        adjust_request = AdjustTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test adjust transaction",
            payload=AdjustTransactionRequestPayload(amount=100),
            issuer="test_user",
        )
        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/adjust",
            json=adjust_request.model_dump(),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == BALANCE_NOT_FOUND_ERROR

    @pytest.mark.parametrize("reset_spent,expected_spent", [(True, 0), (False, 50)])
    async def test_adjust_transaction(
        self, client: AsyncClient, reset_spent, expected_spent
    ):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)

        # First credit the wallet
        credit_request = DepositTransactionRequest(
            credit_type_id=credit_type_id,
            description="Initial credit",
            payload=DepositTransactionRequestPayload(amount=100),
            issuer="test_user",
        )
        await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=credit_request.model_dump(),
        )

        # Create a debit transaction
        debit_request = DebitTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test debit transaction",
            payload=DebitTransactionRequestPayload(amount=50),
            issuer="test_user",
        )
        await client.post(
            f"{self.base_url}/wallets/{wallet_id}/debit",
            json=debit_request.model_dump(),
        )

        # Create an adjust transaction
        adjust_request = AdjustTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test adjust transaction",
            payload=AdjustTransactionRequestPayload(amount=20, reset_spent=reset_spent),
            issuer="test_user",
        )

        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/adjust",
            json=adjust_request.model_dump(),
        )
        assert response.status_code == status.HTTP_200_OK

        # Check the wallet balance
        wallet_response = await client.get(f"{self.base_url}/wallets/{wallet_id}")
        assert wallet_response.status_code == status.HTTP_200_OK
        wallet_data = wallet_response.json()
        balance = self.find_balance(wallet_data["balances"], credit_type_id)
        assert balance is not None
        assert balance.get("available") == 20
        assert balance.get("spent") == expected_spent
        assert balance.get("held") == 0
        assert balance.get("overall_spent") == 50

    async def test_same_transaction_id_twice(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)

        # Create a credit transaction with a specific transaction ID
        transaction_id = "duplicate_test_id" + str(uuid4())
        transaction_request = DepositTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test duplicate transaction",
            payload=DepositTransactionRequestPayload(amount=100),
            issuer="test_user",
            external_id=transaction_id,
        )

        # First attempt should succeed
        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=transaction_request.model_dump(),
        )
        assert response.status_code == status.HTTP_200_OK

        # Second attempt with same transaction ID should fail
        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=transaction_request.model_dump(),
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == DUPLICATE_TRANSACTION_ERROR

        # Try with a different request type but same transaction ID
        debit_request = DebitTransactionRequest(
            credit_type_id=credit_type_id,
            description="Test duplicate transaction with different type",
            payload=DebitTransactionRequestPayload(amount=50),
            issuer="test_user",
            external_id=transaction_id,
        )

        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/debit",
            json=debit_request.model_dump(),
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == DUPLICATE_TRANSACTION_ERROR

    async def test_get_transaction_by_id(self, client: AsyncClient):
        wallet_id, credit_type_id = await self.setup_wallet_and_credit_type(client)

        # Create a credit transaction
        credit_request = DepositTransactionRequest(
            credit_type_id=credit_type_id,
            description="Initial credit",
            payload=DepositTransactionRequestPayload(amount=100),
            issuer="test_user",
        )
        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/deposit",
            json=credit_request.model_dump(),
        )

        transaction_id = response.json()["id"]
        transaction_response = await client.get(
            f"{self.base_url}/transactions/{transaction_id}"
        )
        assert transaction_response.status_code == status.HTTP_200_OK
        assert transaction_response.json()["id"] == transaction_id

    @pytest.mark.parametrize(
        "transaction_type,request_class,payload_class",
        [
            ("deposit", DepositTransactionRequest, DepositTransactionRequestPayload),
            ("debit", DebitTransactionRequest, DebitTransactionRequestPayload),
            ("hold", HoldTransactionRequest, HoldTransactionRequestPayload),
            ("release", ReleaseTransactionRequest, ReleaseTransactionRequestPayload),
            ("adjust", AdjustTransactionRequest, AdjustTransactionRequestPayload),
        ],
    )
    async def test_nonexistent_wallet(
        self, client: AsyncClient, transaction_type, request_class, payload_class
    ):
        wallet_id = str(uuid4())
        credit_type_id = str(uuid4())

        # Prepare payload based on transaction type
        payload_kwargs = (
            {"amount": 100}
            if transaction_type != "release"
            else {"hold_transaction_id": str(uuid4())}
        )

        transaction_request = request_class(
            credit_type_id=credit_type_id,
            description=f"Test {transaction_type} transaction",
            payload=payload_class(**payload_kwargs),
            issuer="test_user",
        )

        response = await client.post(
            f"{self.base_url}/wallets/{wallet_id}/{transaction_type}",
            json=transaction_request.model_dump(),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
