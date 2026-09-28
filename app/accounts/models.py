from pydantic import BaseModel


class BankAccount(BaseModel):
    id: str
    connection_id: str
    user_id: str
    external_id: str
    name: str
    bank_name: str
    account_type: str
    balance: float | None = None