import logging
import sys
from pathlib import Path
from typing import Dict, Any
from app.core.config import Settings

settings = Settings()

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
APP_LOG_FILE = LOGS_DIR / "app.log"
ERROR_LOG_FILE = LOGS_DIR / "error.log"

# Log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
JSON_FORMAT = '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration based on environment."""
    is_production = not settings.DEBUG

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": DEFAULT_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "format": JSON_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": str(APP_LOG_FILE),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": str(ERROR_LOG_FILE),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "level": "ERROR",
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file", "error_file"],
                "level": "INFO" if is_production else "DEBUG",
                "propagate": True,
            },
            "app": {  # Application logger
                "handlers": ["console", "file", "error_file"],
                "level": "INFO" if is_production else "DEBUG",
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console", "file"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }

    # In production, use JSON formatter for file handlers
    if is_production:
        config["handlers"]["file"]["formatter"] = "json"
        config["handlers"]["error_file"]["formatter"] = "json"

    return config


def setup_logging() -> None:
    """Set up logging configuration."""
    import logging.config

    logging.config.dictConfig(get_logging_config())


# Create a logger instance
logger = logging.getLogger("app")
