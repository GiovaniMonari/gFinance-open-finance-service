"""Central pt-BR translation layer for provider payloads.

Everything a user can read that originates from an aggregator is mapped here,
in one place, before it is handed back toward the frontend. Controllers,
services and providers must not carry their own wording.

Technical values are deliberately untouched: identifiers, enum names the app
branches on, API contract fields and provider-specific codes stay exactly as
the provider sent them.
"""

from app.translations.pt_br import (
    translate_account,
    translate_credit_status,
    translate_marketing_name,
    translate_subtype,
    translate_transaction_payload,
)

__all__ = [
    "translate_account",
    "translate_credit_status",
    "translate_marketing_name",
    "translate_subtype",
    "translate_transaction_payload",
]
