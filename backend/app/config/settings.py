"""
ExpenseIQ Application Settings

Centralized configuration management using Pydantic Settings.
"""

from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from the .env file.
    """

    # =====================================================
    # Application Settings
    # =====================================================
    APP_NAME: str = "ExpenseIQ API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Enterprise AI Expense Management Platform"

    DEBUG: bool = True

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # =====================================================
    # PostgreSQL Configuration
    # =====================================================
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DATABASE: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Optional: pin every connection's search_path to a single schema
    # instead of the server default ("$user", public). Unset in every
    # real environment - only the test suite sets this, to isolate
    # itself inside its own schema without needing CREATEDB privilege
    # (see tests/conftest.py).
    POSTGRES_SCHEMA: str | None = None
    GEMINI_API_KEY: str
    GROQ_API_KEY: str
    OLLAMA_HOST: str
    OLLAMA_MODEL: str

    # =====================================================
    # CORS - comma-separated list of allowed frontend origins
    # =====================================================
    CORS_ORIGINS_RAW: str = (
        "http://localhost:5173,http://127.0.0.1:5173"
    )

    # =====================================================
    # JWT Authentication
    # =====================================================
    # Dev-only default - MUST be overridden via .env in any
    # shared/deployed environment (see .env.example).
    JWT_SECRET_KEY: str = "expenseiq-dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS_RAW.split(",")
            if origin.strip()
        ]

    @property
    def DATABASE_URL(self) -> str:
        """
        Build SQLAlchemy connection string dynamically.
        Password is URL encoded to support special characters.
        """

        encoded_password = quote_plus(self.POSTGRES_PASSWORD)

        url = (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:"
            f"{encoded_password}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DATABASE}"
        )

        if self.POSTGRES_SCHEMA:

            search_path_option = quote_plus(
                f"-csearch_path={self.POSTGRES_SCHEMA}"
            )
            url += f"?options={search_path_option}"

        return url

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()