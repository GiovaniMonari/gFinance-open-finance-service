"""pt-BR wording for banking terminology that reaches the user.

Pluggy labels its payload in English. This module is the single place where
that wording becomes natural Brazilian Portuguese, applied at the provider
boundary so every route already carries translated text by the time a response
leaves the service.

Two rules govern every table below:

1. Only display labels are mapped. Identifiers, enum values the app branches
   on (``type``, connection ``status``), ISO currency codes and institution
   names are never touched — they are contracts, not copy.
2. Anything unrecognised passes through untouched. A stray code that we have
   not seen yet is still more truthful than an invented translation, and a
   wrong label on somebody's bank account is worse than an untranslated one.
"""

# Match the key against a table regardless of how the provider spelled it:
# casing, spaces and hyphens are all treated as the same separator.
def _key(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def _normalize(table: dict[str, str]) -> dict[str, str]:
    """Apply the separator rule to the table's own keys.

    Written the way a human would ("Checking Account"), then stored the way
    `_key` will look them up, so the two can never drift apart.
    """
    return {_key(key): value for key, value in table.items()}


def _lookup(value: str | None, table: dict[str, str]) -> str | None:
    if value is None:
        return None

    return table.get(_key(value), value)


# Account subtypes as reported by the aggregator. `account.subtype` is shown
# as the secondary line of every account in the app.
ACCOUNT_SUBTYPES: dict[str, str] = _normalize({
    "checking_account": "Conta corrente",
    "conta_corrente": "Conta corrente",
    "current_account": "Conta corrente",
    "savings_account": "Conta poupança",
    "conta_poupanca": "Conta poupança",
    "salary_account": "Conta salário",
    "conta_salario": "Conta salário",
    "payment_account": "Conta de pagamento",
    "digital_account": "Conta digital",
    "virtual_account": "Conta virtual",
    "money_account": "Conta digital",
    "investment_account": "Investimentos",
    "investimento": "Investimentos",
    "loan_account": "Conta de empréstimo",
    "credit_card": "Cartão de crédito",
    "cartao_de_credito": "Cartão de crédito",
    "prepaid_card": "Cartão pré-pago",
    "debit_card": "Cartão de débito",
    "account": "Conta",
})

# `account.marketingName` is rendered verbatim as the connection caption, so
# an English bank product name is the most visible leak in the whole payload.
MARKETING_NAMES: dict[str, str] = _normalize({
    "checking account": "Conta corrente",
    "current account": "Conta corrente",
    "savings account": "Conta poupança",
    "salary account": "Conta salário",
    "payment account": "Conta de pagamento",
    "digital account": "Conta digital",
    "virtual account": "Conta virtual",
    "money account": "Conta digital",
    "investment account": "Conta de investimentos",
    "loan account": "Conta de empréstimo",
    "credit card": "Cartão de crédito",
    "prepaid card": "Cartão pré-pago",
    "debit card": "Cartão de débito",
    "checking": "Conta corrente",
    "savings": "Conta poupança",
    "credit": "Cartão de crédito",
})

# `account.creditData.status` describes the state of a card contract.
CREDIT_STATUSES: dict[str, str] = _normalize({
    "active": "Ativa",
    "inactive": "Inativa",
    "open": "Aberta",
    "closed": "Encerrada",
    "cancelled": "Cancelada",
    "canceled": "Cancelada",
    "blocked": "Bloqueada",
    "suspended": "Suspensa",
    "expired": "Vencida",
    "overdue": "Em atraso",
    "pending": "Pendente",
    "paid": "Paga",
    "contracted": "Contratada",
    "released": "Liberada",
})

# Merchant categories on transactions. Mirrors the vocabulary the app already
# speaks so a category reads the same wherever it is shown.
TRANSACTION_CATEGORIES: dict[str, str] = _normalize({
    "food_and_drink": "Alimentação",
    "food": "Alimentação",
    "groceries": "Mercado",
    "market": "Mercado",
    "restaurant": "Restaurante",
    "coffee": "Cafeteria",
    "transport": "Transporte",
    "transportation": "Transporte",
    "fuel": "Combustível",
    "gas": "Combustível",
    "gasoline": "Combustível",
    "parking": "Estacionamento",
    "taxi": "Táxi",
    "travel": "Viagem",
    "accommodation": "Hospedagem",
    "hotel": "Hotel",
    "shopping": "Compras",
    "retail": "Compras",
    "health": "Saúde",
    "healthcare": "Saúde",
    "pharmacy": "Farmácia",
    "education": "Educação",
    "entertainment": "Lazer",
    "leisure": "Lazer",
    "services": "Serviços",
    "subscription": "Assinatura",
    "utilities": "Serviços básicos",
    "bills": "Contas",
    "rent": "Aluguel",
    "housing": "Moradia",
    "insurance": "Seguro",
    "transfer": "Transferência",
    "loan": "Empréstimo",
    "salary": "Salário",
    "salary_payment": "Salário",
    "pension": "Aposentadoria",
    "withdrawal": "Saque",
    "deposit": "Depósito",
    "fees": "Taxas",
    "tax": "Impostos",
    "others": "Outros",
    "other": "Outros",
    "uncategorized": "Sem categoria",
})


def translate_subtype(value: str | None) -> str | None:
    return _lookup(value, ACCOUNT_SUBTYPES)


def translate_marketing_name(value: str | None) -> str | None:
    if value is None:
        return None

    return _lookup(value.strip(), MARKETING_NAMES)


def translate_credit_status(value: str | None) -> str | None:
    return _lookup(value, CREDIT_STATUSES)


def translate_transaction(value: str | None) -> str | None:
    return _lookup(value, TRANSACTION_CATEGORIES)


def translate_account(account: dict) -> dict:
    """Return a copy of a provider account with its display labels in pt-BR.

    Balance, ids, ``type`` and ``currency_code`` are copied through unchanged:
    the app compares against them and an ISO currency code is the universally
    understood notation.
    """

    translated = dict(account)

    if account.get("subtype") is not None:
        translated["subtype"] = translate_subtype(account["subtype"])

    if account.get("marketing_name") is not None:
        translated["marketing_name"] = translate_marketing_name(
            account["marketing_name"],
        )

    credit = account.get("credit")

    if isinstance(credit, dict) and credit.get("status") is not None:
        translated["credit"] = {
            **credit,
            "status": translate_credit_status(credit["status"]),
        }

    return translated


def translate_transaction_payload(transaction: dict) -> dict:
    """Return a copy of a provider transaction with its category in pt-BR.

    ``type`` and ``status`` are left alone: both are enum codes the client
    branches on, and the client already renders them.
    """

    if transaction.get("category") is None:
        return transaction

    return {
        **transaction,
        "category": translate_transaction(transaction["category"]),
    }
