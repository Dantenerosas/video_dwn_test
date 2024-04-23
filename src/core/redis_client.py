import json

import redis.asyncio as redis


class RedisClient:
    SET_NAME = "queue"
    TASKS_NAME = "tasks_working"
    TASKS_DONE_NAME = "tasks_done"

    def __init__(self):
        self.connection = redis.Redis(host="localhost", port=6379, db=0)

    async def _set_task(self, queue_name: str, link: str, task: dict | list, ) -> int:
        async with self.connection as connection:
            res = await connection.hset(queue_name, link, json.dumps(task, indent=4).encode('utf-8'))
        return res

    async def _del_task(self, queue_name: str, link: str,) -> int:
        async with self.connection as connection:
            res = await connection.hdel(queue_name, link)
        return res

    async def set_task_to_queue(self, link: str, task: dict | list) -> int:
        res = await self._set_task(queue_name=self.SET_NAME, link=link, task=task)
        return res

    async def get_all_tasks_from_queue(self, queue_name: str) -> dict:
        async with self.connection as connection:
            res = await connection.hgetall(queue_name)
        return res

    async def del_task_from_queue_and_add_to_tasks(self, link: str, task: dict | list) -> int:
        await self._del_task(self.SET_NAME, link)
        return await self._set_task(self.TASKS_NAME, link, task)

    async def del_task_from_tasks_and_add_to_task_done(self, task: dict | list, link: str) -> int:
        await self._del_task(self.TASKS_NAME, link)
        return await self._set_task(self.TASKS_DONE_NAME, link, task)

    async def del_task_from_task_done_queue(self, task) -> int:
        res = await self._del_task(self.TASKS_DONE_NAME, task["link"])
        return res

    async def del_tasks_queue(self) -> int:
        async with self.connection as connection:
            res = await connection.delete(self.TASKS_NAME)
        return res
