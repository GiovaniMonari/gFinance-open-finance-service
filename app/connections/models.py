from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ConnectionStatus(str, Enum):
    PENDING = "pending"
    CONNECTED = "connected"
    ERROR = "error"
    DISCONNECTED = "disconnected"


class BankConnection(BaseModel):
    id: str
    user_id: str
    provider: str
    external_id: str
    status: ConnectionStatus
    last_synced_at: datetime | None = None