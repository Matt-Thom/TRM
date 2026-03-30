"""Application configuration via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_USER: str = "temper"
    DB_PASSWORD: str = "temper"
    DB_NAME: str = "temper"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # JWT
    JWT_SECRET_KEY: str = "dev-secret-change-in-production"
    JWT_ACCESS_TOKEN_TTL: int = 900  # 15 minutes
    JWT_REFRESH_TOKEN_TTL: int = 604800  # 7 days
    JWT_ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # App
    APP_ENV: str = "development"
    DEBUG: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
