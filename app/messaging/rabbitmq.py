import os

import aio_pika
from dotenv import load_dotenv

load_dotenv()


async def connect_rabbitmq():
    url = os.getenv("RABBITMQ_URL")

    connection = await aio_pika.connect_robust(url)

    return connection