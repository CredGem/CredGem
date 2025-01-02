import logging
import sys

from src.core.settings import settings

# Define logging format
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging():
    # Create formatter
    log_level = settings.LOG_LEVEL
    formatter = logging.Formatter(log_format)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    # Set levels for third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("redis").setLevel(logging.INFO)

    if log_level != "DEBUG":
        logging.getLogger('sqlalchemy.engine.Engine').disabled = True
        

    
