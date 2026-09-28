import asyncio
from pathlib import Path
import os

import asyncpg
from dotenv import load_dotenv


load_dotenv()


async def main():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL não configurada")

    migration_path = (
        Path(__file__).parent
        / "app"
        / "database"
        / "002_change_user_id_to_varchar.sql"
    )

    migration = migration_path.read_text(
        encoding="utf-8",
    )

    connection = await asyncpg.connect(database_url)

    try:
        await connection.execute(migration)
        print("Migration 002 aplicada com sucesso.")
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())