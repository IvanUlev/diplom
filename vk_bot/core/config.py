from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Telegram
    API_TOKEN: str
    WEBHOOK_URL: str | None = None
    FRONTEND_URL: str | None = None
    
    @property
    def webhook_path(self) -> str:
        return f"/webhook/{self.API_TOKEN}"

    @property
    def webhook_full_url(self) -> str:
        return f"{self.WEBHOOK_URL}{self.webhook_path}"
    
    
    # PostgreSQL
    PG_HOST: str = "localhost"
    PG_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.PG_HOST}:{self.PG_PORT}/{self.POSTGRES_DB}"
        )
    
    # Server
    WEBAPP_PORT: int = 8080
    
    # Rate limiting
    RATE_LIMIT: str = "29/second"
    
    # Bot settings
    ALLOWED_UPDATES: list[str] = [
        "message", 
        "edited_message", 
        "callback_query", 
        "channel_post"
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()