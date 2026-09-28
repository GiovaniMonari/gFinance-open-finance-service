from pathlib import Path


async def init_db(pool):
    schema_path = Path(__file__).with_name("schema.sql")

    schema = schema_path.read_text(
        encoding="utf-8",
    )

    async with pool.acquire() as connection:
        await connection.execute(schema)