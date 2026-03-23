# bot/config/settings.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_ID: int
    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Railway يوفر هذا تلقائياً
    RAILWAY_PUBLIC_DOMAIN: str = ""
    WEBHOOK_PATH: str = "/webhook"
    PORT: int = 8080
    
    FLOOD_LIMIT: int = 5
    FLOOD_PERIOD: int = 10
    CAPTCHA_TIMEOUT: int = 120
    
    @property
    def WEBHOOK_HOST(self) -> str:
        if self.RAILWAY_PUBLIC_DOMAIN:
            return f"https://{self.RAILWAY_PUBLIC_DOMAIN}"
        # احتياطي
        return os.getenv("RAILWAY_STATIC_URL", "").rstrip('/')
    
    @property
    def WEBHOOK_URL(self) -> str:
        if self.WEBHOOK_HOST:
            return f"{self.WEBHOOK_HOST}{self.WEBHOOK_PATH}"
        return ""
    
    @property
    def IS_WEBHOOK_MODE(self) -> bool:
        return bool(self.WEBHOOK_HOST)
    
    class Config:
        env_file = ".env"


settings = Settings()

# ✅ طباعة للتشخيص (ستظهر في Railway Logs)
print(f"=" * 50)
print(f"🔧 CONFIGURATION:")
print(f"🔧 RAILWAY_PUBLIC_DOMAIN: {settings.RAILWAY_PUBLIC_DOMAIN}")
print(f"🔧 WEBHOOK_HOST: {settings.WEBHOOK_HOST}")
print(f"🔧 WEBHOOK_URL: {settings.WEBHOOK_URL}")
print(f"🔧 IS_WEBHOOK_MODE: {settings.IS_WEBHOOK_MODE}")
print(f"🔧 PORT: {settings.PORT}")
print(f"🔧 DATABASE_URL exists: {bool(settings.DATABASE_URL)}")
print(f"=" * 50)
