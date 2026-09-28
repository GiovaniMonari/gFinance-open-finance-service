import os

import asyncpg
from dotenv import load_dotenv


load_dotenv()


async def connect_postgres():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não configurada"
        )

    return await asyncpg.create_pool(
        database_url,
        min_size=1,
        max_size=5,
    )