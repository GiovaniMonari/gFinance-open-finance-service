from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.connections.exceptions import OpenFinanceError
from app.messaging.rabbitmq import connect_rabbitmq

from app.messaging.publisher import publish_transaction

import asyncio

from app.messaging.consumer import (
    start_consumer,
    start_sync_completed_consumer,
)

from app.synchronization.router import router as synchronization_router

from app.connections.router import router as connections_router

from app.database.postgres import connect_postgres

from app.accounts.router import router as accounts_router

from app.transactions.router import router as transactions_router

from app.messaging.consumer import (
    start_consumer,
    start_sync_completed_consumer,
    start_sync_requested_consumer,
    start_sync_failed_consumer,
)

from app.database.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    connection = await connect_rabbitmq()
    postgres = await connect_postgres()
    await init_db(postgres)

    app.state.rabbitmq = connection
    app.state.postgres = postgres

    consumer_task = asyncio.create_task(
        start_consumer(
            connection,
            postgres,
        )
    )

    sync_completed_task = asyncio.create_task(
        start_sync_completed_consumer(
            connection,
        )
    )

    sync_requested_task = asyncio.create_task(
        start_sync_requested_consumer(
            connection,
            postgres,
        )
    )

    sync_failed_task = asyncio.create_task(
        start_sync_failed_consumer(
            connection,
        )
    )

    yield

    consumer_task.cancel()
    sync_completed_task.cancel()
    sync_requested_task.cancel()
    sync_failed_task.cancel()

    await connection.close()
    await postgres.close()


app = FastAPI(
    title="Econva Open Finance Service",
    lifespan=lifespan,
)

app.include_router(transactions_router)
app.include_router(accounts_router)
app.include_router(connections_router)
app.include_router(synchronization_router)


@app.exception_handler(OpenFinanceError)
async def open_finance_error_handler(
    request,
    error: OpenFinanceError,
):
    """Turn domain errors into one consistent answer.

    Every provider failure travels as an ``OpenFinanceError``, so routes can
    raise them without knowing anything about HTTP and without repeating the
    same try/except. The message is already pt-BR: it is what the user reads.
    """
    return JSONResponse(
        status_code=error.status_code,
        content={
            "status": "error",
            "message": error.detail,
        },
    )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/test/transaction")
async def test_transaction():
    transaction = {
        "transaction_id": "test-001",
        "account_id": "account-001",
        "user_id": "user-001",
        "amount": 150.90,
        "description": "Supermercado",
        "date": "2026-09-26",
        "type": "expense",
        "source": "open_finance",
    }

    await publish_transaction(
        app.state.rabbitmq,
        transaction,
    )

    return {
        "status": "published",
        "transaction": transaction,
    }    