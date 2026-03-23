# bot/config/settings.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str = ""
    ADMIN_ID: int = 0
    DATABASE_URL: str = ""
    REDIS_URL: str = ""
    
    # ✅ Railway يوفر هذا تلقائياً - أو أضفه يدوياً
    RAILWAY_PUBLIC_DOMAIN: str = ""
    PORT: int = 8080
    WEBHOOK_PATH: str = "/webhook"
    
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

# ✅ طباعة للتشخيص
print("=" * 60, flush=True)
print("🔧 SETTINGS:", flush=True)
print(f"   RAILWAY_PUBLIC_DOMAIN: {settings.RAILWAY_PUBLIC_DOMAIN or '❌'}", flush=True)
print(f"   WEBHOOK_HOST: {settings.WEBHOOK_HOST or '❌'}", flush=True)
print(f"   IS_WEBHOOK_MODE: {settings.IS_WEBHOOK_MODE}", flush=True)
print("=" * 60, flush=True)
