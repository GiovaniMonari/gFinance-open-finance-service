from app.normalization.transaction_normalizer import TransactionNormalizer


normalizer = TransactionNormalizer()

transaction = {
    "external_id": "bank-123",
    "amount": 150.90,
    "description": "Supermercado XYZ",
    "date": "2026-09-26",
    "type": "expense",
}

result = normalizer.normalize(
    transaction=transaction,
    user_id="user-001",
    account_id="account-001",
    provider="mock-provider",
)

print(result)