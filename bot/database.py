"""
إدارة قاعدة البيانات PostgreSQL
"""
import asyncpg
from typing import Optional
from bot.config import settings


class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """إنشاء connection pool"""
        self.pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=5,
            max_size=20
        )
        
        # إنشاء الجداول إذا لم تكن موجودة
        await self.create_tables()
    
    async def create_tables(self):
        """إنشاء الجداول الأساسية"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    username VARCHAR(32),
                    first_name VARCHAR(64),
                    last_name VARCHAR(64),
                    is_bot BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    title VARCHAR(128),
                    settings JSONB DEFAULT '{}',
                    welcome_message TEXT DEFAULT 'مرحباً بك في المجموعة!',
                    captcha_enabled BOOLEAN DEFAULT TRUE,
                    max_warnings INT DEFAULT 3,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS warnings (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    group_id BIGINT NOT NULL,
                    reason TEXT,
                    given_by BIGINT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    event_type VARCHAR(32),
                    user_id BIGINT,
                    group_id BIGINT,
                    details JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # إنشاء indexes للأداء
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_warnings_user_group 
                ON warnings(user_id, group_id) WHERE is_active = TRUE
            """)
    
    async def close(self):
        """إغلاق الاتصال"""
        if self.pool:
            await self.pool.close()
    
    # دوال المساعدة
    async def add_user(self, telegram_id: int, username: str, first_name: str, last_name: str = None):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (telegram_id, username, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (telegram_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    updated_at = NOW()
            """, telegram_id, username, first_name, last_name)
    
    async def add_warning(self, user_id: int, group_id: int, reason: str, given_by: int) -> int:
        async with self.pool.acquire() as conn:
            # إضافة الإنذار
            await conn.execute("""
                INSERT INTO warnings (user_id, group_id, reason, given_by)
                VALUES ($1, $2, $3, $4)
            """, user_id, group_id, reason, given_by)
            
            # حساب الإنذارات النشطة
            count = await conn.fetchval("""
                SELECT COUNT(*) FROM warnings 
                WHERE user_id = $1 AND group_id = $2 AND is_active = TRUE
            """, user_id, group_id)
            
            # تسجيل الحدث
            await self.log_event('warning', user_id, group_id, {'reason': reason})
            
            return count
    
    async def remove_warnings(self, user_id: int, group_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE warnings SET is_active = FALSE 
                WHERE user_id = $1 AND group_id = $2
            """, user_id, group_id)
    
    async def log_event(self, event_type: str, user_id: int = None, group_id: int = None, details: dict = None):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO logs (event_type, user_id, group_id, details)
                VALUES ($1, $2, $3, $4)
            """, event_type, user_id, group_id, details or {})


# instance عام
db = Database()

