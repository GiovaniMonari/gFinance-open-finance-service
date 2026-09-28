from fastapi import APIRouter, Request

from app.connections.providers.factory import get_open_finance_provider
from app.normalization.transaction_normalizer import TransactionNormalizer
from app.repositories.account_repository import (
    PostgreSQLAccountRepository,
)
from app.repositories.transaction_repository import (
    PostgreSQLTransactionRepository,
)
from app.transactions.service import TransactionService
from app.repositories.connection_repository import (
    PostgreSQLConnectionRepository,
)
from fastapi import Depends, HTTPException
from app.auth.context import get_user_id
from app.repositories.connection_repository import PostgreSQLConnectionRepository
from app.auth.service_auth import verify_service_token

router = APIRouter(
    prefix="/accounts",
    tags=["Transactions"],
)


def create_transaction_service(request: Request):
    provider = get_open_finance_provider()
    normalizer = TransactionNormalizer()

    account_repository = PostgreSQLAccountRepository(
        request.app.state.postgres
    )

    transaction_repository = PostgreSQLTransactionRepository(
        request.app.state.postgres
    )

    connection_repository = PostgreSQLConnectionRepository(
        request.app.state.postgres
    )

    return TransactionService(
        provider=provider,
        normalizer=normalizer,
        account_repository=account_repository,
        transaction_repository=transaction_repository,
        connection_repository=connection_repository,
    )


@router.post("/{account_id}/transactions/sync")
async def sync_transactions(
    account_id: str,
    request: Request,
    user_id: str = Depends(get_user_id),
    _: bool = Depends(verify_service_token),
):
    account_repository = PostgreSQLAccountRepository(
        request.app.state.postgres
    )

    account = await account_repository.find_by_id(account_id)

    if not account or account.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Conta não encontrada",
        )

    service = create_transaction_service(request)

    transactions = await service.sync_transactions(
        account_id=account_id,
        user_id=user_id,
        rabbitmq_connection=request.app.state.rabbitmq,
        provider_name=service.provider.name,
    )

    return {
        "status": "synchronized",
        "account_id": account_id,
        "transactions": [
            transaction.model_dump(mode="json")
            for transaction in transactions
        ],
    }


@router.get("/{account_id}/transactions")
async def sync_transactions(
    account_id: str,
    request: Request,
    user_id: str = Depends(get_user_id),
    _: bool = Depends(verify_service_token),
):
    account_repository = PostgreSQLAccountRepository(
        request.app.state.postgres
    )

    account = await account_repository.find_by_id(account_id)

    if not account or account.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="Conta não encontrada",
        )

    service = create_transaction_service(request)

    transactions = await service.get_transactions(
        account_id=account_id
    )

    return {
        "status": "success",
        "account_id": account_id,
        "transactions": [
            transaction.model_dump(mode="json")
            for transaction in transactions
        ],
    }