import httpx
import pytest

from src.core.app import app
from src.core.db_config import DBManager
from src.core.redis_config import RedisManager


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def setup_test_environment():
    await DBManager().init_db_connection()
    await RedisManager().connect()

    yield

    await DBManager().disconnect()
    await RedisManager().disconnect()


@pytest.fixture(scope="function")
async def client(setup_test_environment):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as test_client:
        yield test_client
