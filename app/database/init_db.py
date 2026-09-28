import asyncio

from app.database.postgres import connect_postgres


async def init_db():
    pool = await connect_postgres()

    try:
        with open(
            "app/database/schema.sql",
            "r",
            encoding="utf-8",
        ) as file:
            schema = file.read()

        async with pool.acquire() as connection:
            await connection.execute(schema)

    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(init_db())