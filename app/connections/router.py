from fastapi import APIRouter

from app.connections.providers.factory import get_open_finance_provider
from app.connections.service import ConnectionService
from app.repositories.connection_repository import (
    PostgreSQLConnectionRepository,
)
from fastapi import APIRouter, Request

from fastapi import Depends
from app.auth.context import get_user_id
from app.auth.service_auth import verify_service_token
from app.connections.providers.pluggy import PluggyClient

from pydantic import BaseModel

router = APIRouter(
    prefix="/connections",
    tags=["Connections"],
)

class PluggyConnectionRequest(BaseModel):
    item_id: str

@router.post("/pluggy/connect")
async def connect_pluggy(
    data: PluggyConnectionRequest,
    request: Request,
    user_id: str = Depends(get_user_id),
    _: bool = Depends(verify_service_token),
):
    repository = PostgreSQLConnectionRepository(
        request.app.state.postgres
    )

    provider = get_open_finance_provider(
        connection_repository=repository
    )

    if provider.name != "pluggy":
        raise HTTPException(
            status_code=400,
            detail="Provider Pluggy não está ativo",
        )

    service = ConnectionService(
        provider=provider,
        repository=repository,
    )

    connection = await service.create_connection(
        user_id=user_id,
        item_id=data.item_id,
    )

    return {
        "status": "connected",
        "connection": connection.model_dump(mode="json"),
    }

@router.post("")
async def create_connection(
    request: Request,
):
    user_id = "00000000-0000-0000-0000-000000000001"

    connection_repository = PostgreSQLConnectionRepository(
        request.app.state.postgres
    )

    provider = get_open_finance_provider(
        connection_repository=connection_repository
    )

    repository = PostgreSQLConnectionRepository(
        request.app.state.postgres
    )

    service = ConnectionService(
        provider=provider,
        repository=repository,
    )

    connection = await service.create_connection(
        user_id=user_id,
    )

    return {
        "status": "created",
        "connection": connection,
    }

@router.get("")
async def get_connections(
    request: Request,
    user_id: str = Depends(get_user_id),
    _: bool = Depends(verify_service_token),
):
    repository = PostgreSQLConnectionRepository(
        request.app.state.postgres
    )

    connections = await repository.find_by_user_id(user_id)

    return {
        "status": "found",
        "connections": [
            connection.model_dump(mode="json")
            for connection in connections
        ],
    }

@router.get("/{connection_id}")
async def get_connection(
    connection_id: str,
    request: Request,
):
    repository = PostgreSQLConnectionRepository(
        request.app.state.postgres
    )

    connection = await repository.find_by_id(
        connection_id
    )

    if not connection:
        return {
            "status": "not_found",
            "connection": None,
        }

    return {
        "status": "found",
        "connection": connection,
    }

@router.post("/pluggy/connect-token")
async def create_pluggy_connect_token(
    user_id: str = Depends(get_user_id),
    _: bool = Depends(verify_service_token),
):
    client = PluggyClient()

    token = await client.create_connect_token(
        client_user_id=user_id,
    )

    return {
        "status": "success",
        "connect_token": token,
    }