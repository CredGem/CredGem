from logging import getLogger
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Any:
        try:
            return await call_next(request)
        except Exception as e:
            return await self.handle_error(e, request)

    async def handle_error(self, exc: Exception, request: Request) -> Any:
        if isinstance(exc, HTTPException):
            raise exc

        # Log detailed error information
        logger.error(
            "Request failed with unhandled exception",
            exc_info=True,
        )

        # Return JSON response instead of raising an exception
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )


def setup_error_handlers(app: FastAPI) -> None:
    app.add_middleware(ErrorHandlerMiddleware)
