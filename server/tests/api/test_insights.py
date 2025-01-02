from datetime import datetime, timedelta, timezone

import httpx
import pytest

from scripts.load_seed_data import load_seed_data
from src.core.settings import settings
from src.models.Insights import TimeGranularity

pytestmark = pytest.mark.anyio


class TestInsightsEndpoints:
    base_url = settings.API_V1_STR

    @pytest.fixture(autouse=True, scope="class")
    async def setup_test_data(self):
        # Load seed data before running tests
        await load_seed_data(clear_existing=True)

    @pytest.mark.parametrize(
        "granularity",
        [
            TimeGranularity.DAY.value,
            TimeGranularity.WEEK.value,
            TimeGranularity.MONTH.value,
        ],
    )
    async def test_get_wallet_activity(
        self, client: httpx.AsyncClient, granularity: str
    ):
        # Test getting wallet activity
        end_date = datetime.now(tz=timezone.utc)
        start_date = end_date - timedelta(days=365)

        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "granularity": granularity,
        }

        response = await client.get(
            f"{self.base_url}/insights/wallets/activity", params=params
        )
        assert response.status_code == 200

    async def test_wallet_activity_date_range(self, client: httpx.AsyncClient):
        # Test that all results fall within the specified date range
        end_date = datetime.now(tz=timezone.utc)
        start_date = end_date - timedelta(days=365)

        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "granularity": TimeGranularity.DAY.value,
        }

        response = await client.get(
            f"{self.base_url}/insights/wallets/activity", params=params
        )
        assert response.status_code == 200
        data = response.json()

        # Verify each data point falls within the requested date range
        for point in data["points"]:
            timestamp = point["timestamp"]
            # Replace 'Z' with '+00:00' for proper ISO format parsing
            timestamp = timestamp.replace("Z", "+00:00")
            point_date = datetime.fromisoformat(timestamp)
            assert start_date <= point_date <= end_date

    async def test_get_trending_wallets(self, client: httpx.AsyncClient):
        # Test getting trending wallets
        end_date = datetime.now(tz=timezone.utc)
        start_date = end_date - timedelta(days=365)
        limit = 5

        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "limit": limit,
        }

        response = await client.get(
            f"{self.base_url}/insights/wallets/trending", params=params
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= limit

    async def test_get_credit_usage(self, client: httpx.AsyncClient):
        # Test getting credit usage summary
        end_date = datetime.now(tz=timezone.utc)
        start_date = end_date - timedelta(days=365)

        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

        response = await client.get(
            f"{self.base_url}/insights/credits/usage-summary", params=params
        )
        assert response.status_code == 200

    async def test_get_credit_usage_timeseries(self, client: httpx.AsyncClient):
        # Test getting credit usage timeseries
        end_date = datetime.now(tz=timezone.utc)
        start_date = end_date - timedelta(days=365)

        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "granularity": TimeGranularity.DAY.value,
        }

        response = await client.get(
            f"{self.base_url}/insights/credits/usage-timeseries", params=params
        )
        assert response.status_code == 200

    async def test_invalid_granularity(self, client: httpx.AsyncClient):
        # Test with invalid granularity
        end_date = datetime.now(tz=timezone.utc)
        start_date = end_date - timedelta(days=365)

        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "granularity": "INVALID_GRANULARITY",
            "context": "[user_id=test_user]",
        }

        response = await client.get(
            f"{self.base_url}/insights/wallets/activity", params=params
        )
        assert response.status_code == 422  # Should return validation error

    async def test_invalid_limit(self, client: httpx.AsyncClient):
        # Test with invalid limit for trending wallets
        end_date = datetime.now(tz=timezone.utc)
        start_date = end_date - timedelta(days=365)

        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "limit": -1,  # Invalid limit
        }

        response = await client.get(
            f"{self.base_url}/insights/wallets/trending", params=params
        )
        assert response.status_code == 422  # Should return validation error

    async def test_get_wallet_activity_with_invalid_date_range(
        self, client: httpx.AsyncClient
    ):
        # Test with invalid date range
        end_date = datetime.now(tz=timezone.utc)
        start_date = end_date + timedelta(days=1)

        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }

        response = await client.get(
            f"{self.base_url}/insights/wallets/activity", params=params
        )
        assert response.status_code == 422  # Should return validation error
