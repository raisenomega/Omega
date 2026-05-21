"""Access control helper · cliente propio O reseller dueño.

Compartido entre GET y PATCH /onboarding-data (DRY).
"""
from typing import Any
from app.api.routes.clients_v3 import _clients_reader as reader


def user_owns_client(user_id: str, client: dict[str, Any]) -> bool:
    if str(client.get("user_id") or "") == user_id:
        return True
    reseller_id = str(client.get("reseller_id") or "")
    if not reseller_id:
        return False
    return reseller_id in reader.get_user_reseller_ids(user_id)
