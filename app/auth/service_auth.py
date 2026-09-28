import os

from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()


async def verify_service_token(
    authorization: str = Header(...),
):
    expected_token = os.getenv("INTERNAL_SERVICE_TOKEN")

    if not expected_token:
        raise RuntimeError(
            "INTERNAL_SERVICE_TOKEN não configurado"
        )

    if authorization != f"Bearer {expected_token}":
        raise HTTPException(
            status_code=401,
            detail="Token de serviço inválido",
        )

    return True