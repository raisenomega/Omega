"""Resolver de client (target) para handlers de Content Lab · DEBT-CL-005.

Si request.client_id presente → lookup explícito + access control vía
user_owns_client. Si no → fallback al cliente propio del user (legacy).

cross-BC helper · candidato a app.shared.access_control en refactor futuro
(hoy: _clients_reader.get_client + _access_control.user_owns_client son
helpers puros sin imports externos · pragmático importar desde clients_v3).
"""
from typing import Any, Optional
from fastapi import HTTPException

# cross-BC helper · candidato a app.shared.access_control
from app.api.routes.clients_v3 import _clients_reader as clients_reader
from app.api.routes.clients_v3._access_control import user_owns_client

from app.api.routes.content_lab_v3 import _content_lab_repository as repo


def resolve_client_or_403(user_id: str, request_client_id: Optional[str]) -> dict[str, Any]:
    """Retorna client dict · raise HTTPException 403/404 si no autorizado o inexistente.

    DEBT-CL-005: prioridad payload.client_id (multi-client reseller) → fallback
    find_client_for_user (legacy single-client owner).
    """
    if request_client_id:
        client = clients_reader.get_client(request_client_id)
        if not client:
            raise HTTPException(status_code=404, detail="client_not_found")
        if not user_owns_client(user_id, client):
            raise HTTPException(status_code=403, detail="client_access_denied")
        return client
    # Fallback legacy · cliente propio del user (caso owner sin reseller flow)
    client = repo.find_client_for_user(user_id)
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    return client
