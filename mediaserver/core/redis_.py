import asyncio
from typing import Dict, Union

import aioredis
import ujson

from .settings import settings


async def create_pool():
    global conn
    conn = await aioredis.create_redis_pool(settings.redis_url)


asyncio.run(create_pool())


async def close_redis():
    conn.close()
    await conn.wait_closed()


async def load_data(file_id: str) -> Dict[str, Union[str, int, None]]:
    file = await conn.get(file_id, encoding="utf-8")
    return ujson.loads(file)


async def dump_data(file_id: str, file_data: Dict[str, Union[str, int, None]]) -> None:
    await conn.set(
        file_id,
        ujson.dumps(file_data),
    )
    await conn.expire(file_id, 24 * 60 * 60)


async def remove_data(file_id: str) -> None:
    await conn.delete(file_id)
