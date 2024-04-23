import asyncio
import json
from functools import partial

from aio_pika import connect, Message, DeliveryMode
from aio_pika.abc import AbstractIncomingMessage


async def on_message(message: AbstractIncomingMessage, queue) -> None:
    async with message.process():
        await queue.put(json.loads(message.body))
        print(f"     Message body is: {message.body!r}")


async def get_messages(inner_queue) -> None:
    async with await connect("amqp://guest:guest@localhost/") as connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(
            "hello",
            durable=True,
        )

        await queue.consume(partial(on_message, queue=inner_queue))

        print(" [*] Waiting for messages. To exit press CTRL+C")
        await asyncio.Future()


async def publish_message_with_task_done(task: dict | list) -> None:
    queue_name = "tasks_done"
    async with await connect("amqp://guest:guest@localhost/") as connection:
        # Creating channel
        channel = await connection.channel()

        # Will take no more than 10 messages in advance
        await channel.set_qos(prefetch_count=1)

        # Declaring queue
        queue = await channel.declare_queue(queue_name)
        message = Message(
            json.dumps(task, indent=4).encode('utf-8'), delivery_mode=DeliveryMode.PERSISTENT,
        )
        await channel.default_exchange.publish(
            message,
            routing_key=queue_name,
        )

