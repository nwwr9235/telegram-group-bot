from bot.database.connection import get_pool

async def add_warning(user_id: int, group_id: int, reason: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO warnings (user_id, group_id, reason) VALUES ($1, $2, $3)",
            user_id, group_id, reason
        )
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM warnings WHERE user_id = $1 AND group_id = $2",
            user_id, group_id
        )
        return count

async def remove_warnings(user_id: int, group_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM warnings WHERE user_id = $1 AND group_id = $2",
            user_id, group_id
        )

async def get_group_settings(group_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM groups WHERE telegram_id = $1", group_id
        )
        return row

