"""
إعدادات البوت - تُحمل من متغيرات البيئة
"""
import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str
    ADMIN_ID: int  # معرف المطور للواجهة المتقدمة
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost/dbname"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Webhook (Railway)
    WEBHOOK_HOST: str = ""  # يُملأ تلقائياً من RAILWAY_PUBLIC_DOMAIN
    WEBHOOK_PATH: str = "/webhook"
    PORT: int = 8080
    
    # Anti-flood
    FLOOD_LIMIT: int = 5  # رسائل
    FLOOD_PERIOD: int = 10  # ثواني
    FLOOD_BAN_DURATION: int = 300  # 5 دقائق
    
    # CAPTCHA
    CAPTCHA_TIMEOUT: int = 120  # ثانية
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# تحميل الإعدادات
settings = Settings()

# تعيين WEBHOOK_HOST من Railway إذا متوفر
if os.getenv("RAILWAY_PUBLIC_DOMAIN"):
    settings.WEBHOOK_HOST = f"https://{os.getenv('RAILWAY_PUBLIC_DOMAIN')}"

