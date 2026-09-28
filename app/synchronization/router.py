import uuid


from app.synchronization.models import (
    SynchronizationJob,
    SyncStatus,
)
from app.repositories.sync_repository import (
    PostgreSQLSynchronizationRepository,
)

from fastapi import APIRouter, Request, HTTPException, Depends

from app.auth.context import get_user_id

from app.connections.providers.factory import get_open_finance_provider
from app.repositories.connection_repository import (
    PostgreSQLConnectionRepository,
)
from app.repositories.account_repository import (
    PostgreSQLAccountRepository,
)
from app.repositories.transaction_repository import (
    PostgreSQLTransactionRepository,
)
from app.normalization.transaction_normalizer import TransactionNormalizer
from app.transactions.service import TransactionService
from app.synchronization.service import SynchronizationService

from app.messaging.publisher import publish_event
from app.messaging.events import EventType

from app.auth.service_auth import verify_service_token

router = APIRouter(
    prefix="/connections",
    tags=["Synchronization"],
)


@router.post("/{connection_id}/sync")
async def sync_connection(
    connection_id: str,
    request: Request,
    user_id: str = Depends(get_user_id),
    _: bool = Depends(verify_service_token),
):
    connection_repository = PostgreSQLConnectionRepository(
        request.app.state.postgres
    )

    provider = get_open_finance_provider(
        connection_repository=connection_repository
    )

    connection_repository = PostgreSQLConnectionRepository(
        request.app.state.postgres
    )

    account_repository = PostgreSQLAccountRepository(
        request.app.state.postgres
    )

    transaction_repository = PostgreSQLTransactionRepository(
        request.app.state.postgres
    )

    transaction_service = TransactionService(
        provider=provider,
        normalizer=TransactionNormalizer(),
        account_repository=account_repository,
        transaction_repository=transaction_repository,
        connection_repository=connection_repository,
    )

    synchronization_service = SynchronizationService(
        provider=provider,
        connection_repository=connection_repository,
        account_repository=account_repository,
        transaction_service=transaction_service,
    )

    connection = await connection_repository.find_by_id_and_user_id(
        connection_id=connection_id,
        user_id=user_id,
    )

    if not connection:
        raise HTTPException(
            status_code=404,
            detail="Conexão não encontrada",
        )

    result = await synchronization_service.sync_connection(
        connection_id=connection_id,
        user_id=user_id,
        rabbitmq_connection=request.app.state.rabbitmq,
        job_id=str(uuid.uuid4()),
    )

    return {
        "status": "synchronized",
        "connection_id": connection_id,
        "accounts": [
            account.model_dump(mode="json")
            for account in result["accounts"]
        ],
        "transactions": [
            transaction.model_dump(mode="json")
            for transaction in result["transactions"]
        ],
    }

@router.post("/{connection_id}/sync/request")
async def request_sync(
    connection_id: str,
    request: Request,
    user_id: str = Depends(get_user_id),
    _: bool = Depends(verify_service_token),
):

    sync_repository = PostgreSQLSynchronizationRepository(
        request.app.state.postgres
    )

    active_job = await sync_repository.find_active_by_connection_id(
        connection_id
    )

    if active_job:
        return {
            "status": "already_processing",
            "job_id": active_job.id,
            "connection_id": connection_id,
            "job_status": active_job.status.value,
        }

    connection_repository = PostgreSQLConnectionRepository(
        request.app.state.postgres
    )

    connection = await connection_repository.find_by_id_and_user_id(
        connection_id=connection_id,
        user_id=user_id,
    )

    if not connection:
        raise HTTPException(
            status_code=404,
            detail="Conexão não encontrada",
        )

    job = SynchronizationJob(
        id=str(uuid.uuid4()),
        connection_id=connection_id,
        user_id=user_id,
        status=SyncStatus.PENDING,
    )

    await sync_repository.create(job)

    await publish_event(
        connection=request.app.state.rabbitmq,
        event_type=EventType.ACCOUNT_SYNC_REQUESTED,
        payload={
            "job_id": job.id,
            "connection_id": connection_id,
            "user_id": user_id,
        },
    )

    return {
        "status": "sync_requested",
        "job_id": job.id,
        "connection_id": connection_id,
    }

@router.get("/sync/{job_id}")
async def get_sync_status(
    job_id: str,
    request: Request,
    user_id: str = Depends(get_user_id),
):
    sync_repository = PostgreSQLSynchronizationRepository(
        request.app.state.postgres
    )

    job = await sync_repository.find_by_id_and_user_id(
        job_id=job_id,
        user_id=user_id,
    )

    if not job:
        return {
            "status": "not_found",
            "job": None,
        }

    return {
        "status": "success",
        "job": job.model_dump(mode="json"),
    }

@router.get("/{connection_id}/sync/history")
async def get_sync_history(
    connection_id: str,
    request: Request,
    user_id: str = Depends(get_user_id),
    _: bool = Depends(verify_service_token),
):

    connection_repository = PostgreSQLConnectionRepository(
        request.app.state.postgres
    )

    connection = await connection_repository.find_by_id_and_user_id(
        connection_id=connection_id,
        user_id=user_id,
    )

    if not connection:
        raise HTTPException(
            status_code=404,
            detail="Conexão não encontrada",
        )

    sync_repository = PostgreSQLSynchronizationRepository(
        request.app.state.postgres
    )

    jobs = await sync_repository.find_by_connection_id(
        connection_id
    )

    return {
        "status": "success",
        "connection_id": connection_id,
        "jobs": [
            job.model_dump(mode="json")
            for job in jobs
        ],
    }