from enum import Enum


class EventType(str, Enum):
    ACCOUNT_SYNC_REQUESTED = "account.sync.requested"
    ACCOUNT_SYNC_COMPLETED = "account.sync.completed"
    ACCOUNT_SYNC_FAILED = "account.sync.failed"