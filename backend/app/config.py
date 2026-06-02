from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # --- Project ---
    PROJECT_NAME: str = "ReconCTRL"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # --- PostgreSQL ---
    POSTGRES_DB: str = "reconctrl"
    POSTGRES_USER: str = "recon"
    POSTGRES_PASSWORD: str = "reconpassword123"
    DATABASE_URL: str = "postgresql+asyncpg://recon:reconpassword123@postgres:5432/reconctrl"

    # --- Redis ---
    REDIS_URL: str = "redis://redis:6379/0"

    # --- Security / JWT ---
    SECRET_KEY: str = "changeme"
    JWT_SECRET_KEY: str = "changeme"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # --- CORS ---
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # --- Optional / AI ---
    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-5-haiku-20241022"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
