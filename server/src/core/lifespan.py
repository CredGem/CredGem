from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.db_config import DBManager
from src.core.logging_config import setup_logging
from src.core.redis_config import RedisManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    # Startup
    await DBManager().init_db_connection()
    await RedisManager().connect()

    yield

    # Shutdown
    await DBManager().disconnect()
    await RedisManager().disconnect()
