import asyncpg
from bot.config.settings import settings

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=5, max_size=20)
    
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

async def close_db():
    if pool:
        await pool.close()

async def get_pool():
    return pool
