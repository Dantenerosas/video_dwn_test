import asyncio

from src.core.redis_client import RedisClient

redis = RedisClient()


class AsyncQueue(asyncio.Queue):

    async def put(self, item):
        await redis.set_task_to_queue(item["link"], item)
        return await super().put(item)
