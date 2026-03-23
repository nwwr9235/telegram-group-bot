# bot/config/settings.py
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str = ""  # قيمة افتراضية فارغة للتشخيص
    ADMIN_ID: int = 0
    
    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    
    RAILWAY_PUBLIC_DOMAIN: str = ""
    WEBHOOK_PATH: str = "/webhook"
    PORT: int = 8080
    
    FLOOD_LIMIT: int = 5
    FLOOD_PERIOD: int = 10
    CAPTCHA_TIMEOUT: int = 120
    
    @property
    def WEBHOOK_HOST(self) -> str:
        # طرق متعددة للحصول على النطاق
        if self.RAILWAY_PUBLIC_DOMAIN:
            return f"https://{self.RAILWAY_PUBLIC_DOMAIN}"
        
        # احتياطي: Railway Static URL
        static_url = os.getenv("RAILWAY_STATIC_URL", "")
        if static_url:
            return static_url.rstrip('/')
        
        # احتياطي: Railway URL
        railway_url = os.getenv("RAILWAY_URL", "")
        if railway_url:
            return railway_url.rstrip('/')
        
        return ""
    
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
        case_sensitive = False  # غير حساس لحالة الأحرف


# إنشاء instance
settings = Settings()

# طباعة للتشخيص
print("=" * 60, flush=True)
print("🔧 SETTINGS DIAGNOSTICS:", flush=True)
print(f"   BOT_TOKEN: {'✅ Set' if settings.BOT_TOKEN else '❌ Missing'}", flush=True)
print(f"   ADMIN_ID: {settings.ADMIN_ID}", flush=True)
print(f"   RAILWAY_PUBLIC_DOMAIN: {settings.RAILWAY_PUBLIC_DOMAIN or '❌ Missing'}", flush=True)
print(f"   WEBHOOK_HOST: {settings.WEBHOOK_HOST or '❌ Missing'}", flush=True)
print(f"   WEBHOOK_URL: {settings.WEBHOOK_URL or '❌ Missing'}", flush=True)
print(f"   IS_WEBHOOK_MODE: {settings.IS_WEBHOOK_MODE}", flush=True)
print(f"   DATABASE_URL: {'✅ Set' if settings.DATABASE_URL else '❌ Missing'}", flush=True)
print("=" * 60, flush=True)
