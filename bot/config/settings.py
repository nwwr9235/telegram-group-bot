import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_ID: int
    DATABASE_URL: str = "postgresql://user:pass@localhost/dbname"
    REDIS_URL: str = "redis://localhost:6379/0"
    WEBHOOK_HOST: str = ""
    WEBHOOK_PATH: str = "/webhook"
    PORT: int = 8080
    FLOOD_LIMIT: int = 5
    FLOOD_PERIOD: int = 10
    CAPTCHA_TIMEOUT: int = 120

    class Config:
        env_file = ".env"

settings = Settings()

if os.getenv("RAILWAY_PUBLIC_DOMAIN"):
    settings.WEBHOOK_HOST = f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}"
