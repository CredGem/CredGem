import uvicorn

from src.core.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        app="src.core.app:app",
        host="0.0.0.0",
        log_level="info",
        port=int(settings.PORT),
    )
