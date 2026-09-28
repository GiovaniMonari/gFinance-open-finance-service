from enum import Enum

from pydantic import BaseModel


class SyncStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SynchronizationJob(BaseModel):
    id: str
    connection_id: str
    user_id: str
    status: SyncStatus
    accounts_count: int = 0
    transactions_count: int = 0
    error: str | None = None