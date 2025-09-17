import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Application
    PROJECT_NAME: str = "ticketio-backend"
    VERSION: str = "0.0.1"
    API_V1_STR: str = "/v1"
    DEBUG: bool = os.getenv("DEBUG") or True

    DATABASE_USER: str = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD")
    DATABASE_HOST: str = os.getenv("DATABASE_HOST")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", 5432)
    DATABASE_DB: str = os.getenv("DATABASE_DB")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.data.get("DATABASE_USER"),
            password=values.data.get("DATABASE_PASSWORD"),
            host=values.data.get("DATABASE_HOST"),
            port=int(values.data.get("DATABASE_PORT", 5432)),
            path=f"{values.data.get('DATABASE_DB')}",
        )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Session settings
    SESSION_EXPIRE_SECONDS: int = 3600  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1  # day

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = os.getenv("BACKEND_CORS_ORIGINS")
