from app.transactions.models import BankTransaction


class TransactionNormalizer:

    def normalize(
        self,
        transaction: dict,
        user_id: str,
        account_id: str,
        provider: str,
    ) -> BankTransaction:

        return BankTransaction(
            external_id=transaction["external_id"],
            account_id=account_id,
            user_id=user_id,
            amount=transaction["amount"],
            description=transaction["description"],
            date=transaction["date"],
            type=transaction["type"],
            category=transaction.get("category"),
            provider=provider,
            source="open_finance",
        )