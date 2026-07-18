"""
Centralized application configuration.

All environment variables are read ONCE here via pydantic-settings.
No other module should call os.getenv() directly — they should import
`settings` from this file instead. This keeps config in one place and
makes it trivial to see every env var the app depends on.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os


class Settings(BaseSettings):
    # --- App metadata ---
    APP_NAME: str = "AI Resume Analyzer"
    APP_ENV: str = "development"  # development | production
    API_PREFIX: str = "/api"

    # --- CORS ---
    # Comma-separated list of allowed origins, e.g. "http://localhost:5173,https://mydomain.com"
    CORS_ORIGINS: str = "http://localhost:5173"

    # --- Gemini API ---
    load_dotenv()
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL")

    # --- Upload limits ---
    MAX_UPLOAD_SIZE_MB: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor.
    Using lru_cache means the .env file is parsed only once per process,
    and the same Settings instance is reused everywhere (cheap + consistent).
    """
    return Settings()


settings = get_settings()
