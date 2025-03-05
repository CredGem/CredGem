from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.error_handlers import setup_error_handlers
from src.core.lifespan import lifespan
from src.core.settings import settings
from src.routes import router as router_v1

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

setup_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS_LIST,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}


@app.get("/", tags=["health"])
async def root():
    return {"message": "Welcome to CredGem API"}


app.include_router(router_v1, prefix=settings.API_V1_STR)
