from datetime import date

from pydantic import BaseModel


class BankTransaction(BaseModel):
    external_id: str
    account_id: str
    user_id: str
    amount: float
    description: str
    date: date
    type: str
    category: str | None = None
    provider: str
    source: str