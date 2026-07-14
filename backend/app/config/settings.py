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
    GEMINI_API_KEY: str
    GROQ_API_KEY: str
    OLLAMA_HOST: str
    OLLAMA_MODEL: str

    @property
    def DATABASE_URL(self) -> str:
        """
        Build SQLAlchemy connection string dynamically.
        Password is URL encoded to support special characters.
        """

        encoded_password = quote_plus(self.POSTGRES_PASSWORD)

        return (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:"
            f"{encoded_password}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DATABASE}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()