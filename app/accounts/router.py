from fastapi import APIRouter, Request

from app.accounts.service import AccountService
from app.connections.providers.factory import get_open_finance_provider
from app.repositories.account_repository import (
    PostgreSQLAccountRepository,
)

from fastapi import Depends
from app.auth.context import get_user_id
from fastapi import HTTPException
from app.repositories.connection_repository import PostgreSQLConnectionRepository
from app.auth.service_auth import verify_service_token

router = APIRouter(
    prefix="/connections",
    tags=["Accounts"],
)


@router.post("/{connection_id}/accounts/sync")
async def sync_accounts(
    connection_id: str,
    request: Request,
    user_id: str = Depends(get_user_id),
    _: bool = Depends(verify_service_token),
):
    provider = get_open_finance_provider()

    repository = PostgreSQLAccountRepository(
        request.app.state.postgres
    )

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

    service = AccountService(
        provider=provider,
        repository=repository,
    )

    accounts = await service.sync_accounts(
        connection_id=connection_id,
        user_id=user_id,
    )

    return {
        "status": "synchronized",
        "connection_id": connection_id,
        "accounts": [
            account.model_dump(mode="json")
            for account in accounts
        ],
    }