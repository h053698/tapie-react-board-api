from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Board"
    SECRET_KEY: str = "your-secret-key-here"  # In production, use environment variable
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DATABASE_URL: str = "sqlite://db.sqlite3"
    
    # Cookie settings
    COOKIE_NAME: str = "session"
    COOKIE_DOMAIN: Optional[str] = None
    COOKIE_SECURE: bool = False  # Set to True in production with HTTPS
    COOKIE_SAMESITE: str = "lax"

    class Config:
        case_sensitive = True


settings = Settings()
