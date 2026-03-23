# bot/database/connection.py
import asyncpg
import logging
from bot.config.settings import settings

logger = logging.getLogger(__name__)
pool = None

async def init_db():
    """إنشاء connection pool"""
    global pool
    
    if not settings.DATABASE_URL:
        logger.warning("⚠️ DATABASE_URL not set, skipping DB")
        return
    
    try:
        logger.info(f"🔄 Connecting to database...")
        pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=1,
            max_size=5,
            command_timeout=30,
            server_settings={
                'jit': 'off'  # لتجنب مشاكل Railway
            }
        )
        
        # إنشاء الجداول
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    telegram_id BIGINT PRIMARY KEY,
                    title TEXT,
                    welcome_text TEXT DEFAULT 'مرحباً بك!',
                    max_warnings INT DEFAULT 3
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS warnings (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    group_id BIGINT,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
        
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # لا نرفع الخطأ - البوت يعمل بدون DB مؤقتاً

async def close_db():
    """إغلاق الاتصال"""
    global pool
    if pool:
        await pool.close()
        pool = None

async def get_pool():
    """الحصول على pool"""
    if pool is None:
        raise Exception("Database not initialized")
    return pool
