import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db_config import DBManager
from src.models.base import DBModel


class DBSessionCtx:
    def __init__(
        self,
        session: AsyncSession,
        commit_on_success: bool = True,
        rollback_on_error: bool = True,
    ):
        self.session = session
        self.commit_on_success = commit_on_success
        self.rollback_on_error = rollback_on_error
        self.objects_to_refresh = []

    def add_to_refresh(self, objects: list[DBModel]):
        self.objects_to_refresh.extend(objects)


@asynccontextmanager
async def db_session(
    read_only: bool = False,
    commit_on_success: bool = True,
    rollback_on_error: bool = True,
) -> AsyncGenerator[DBSessionCtx, None]:
    async with DBManager().AsyncSessionMaker() as session:
        try:
            ctx = DBSessionCtx(session, commit_on_success, rollback_on_error)
            yield ctx
            if commit_on_success and not read_only:
                await session.commit()
            if ctx.objects_to_refresh and not read_only:
                await asyncio.gather(
                    *(session.refresh(obj) for obj in ctx.objects_to_refresh)
                )
        except Exception as e:
            if rollback_on_error and not read_only:
                await session.rollback()
            raise e
        finally:
            await session.close()
