import json
import aio_pika
from aio_pika import Message

from app.messaging.events import EventType


async def publish_transaction(
    connection,
    transaction: dict,
):
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "Econva.events",
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )

    queue = await channel.declare_queue(
        "transactions",
        durable=True,
    )

    await queue.bind(
        exchange,
        routing_key="transaction.created",
    )

    message = Message(
        body=json.dumps(transaction).encode(),
        content_type="application/json",
    )

    await exchange.publish(
        message,
        routing_key="transaction.created",
    )

    await channel.close()


async def publish_event(
    connection,
    event_type: EventType,
    payload: dict,
):
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "Econva.events",
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )

    message = Message(
        body=json.dumps(payload).encode(),
        content_type="application/json",
    )

    await exchange.publish(
        message,
        routing_key=event_type.value,
    )

    await channel.close()