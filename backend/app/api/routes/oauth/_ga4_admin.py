"""GA4 Admin API · lista las propiedades GA4 del cliente conectado (Vía A · picker).

Contrato OFICIAL verificado (developers.google.com · accountSummaries.list):
  GET https://analyticsadmin.googleapis.com/v1beta/accountSummaries (pageSize≤200) ->
  {accountSummaries: [{displayName, propertySummaries: [{property: "properties/<id>", displayName}]}]}.
Scope analytics.readonly (ya en GOOGLE_SCOPES) ALCANZA · NO escribe nada. Best-effort + honesto
(sin token -> [] · API falla -> [] · NUNCA levanta · regla cero-mocks)."""
import logging

import httpx

from app.api.routes.oauth._oauth_token_repository import get_token

logger = logging.getLogger(__name__)

_ADMIN_URL = "https://analyticsadmin.googleapis.com/v1beta/accountSummaries"
_HTTP_TIMEOUT = 12.0


async def list_ga4_properties(client_id: str) -> list[dict[str, str]]:
    """Token Google del cliente -> [{property_id, display_name}] de sus propiedades GA4.
    [] honesto si no hay token / no hay propiedades / la API falla."""
    try:
        token = await get_token(client_id, "google")
    except Exception as e:  # noqa: BLE001 · crypto/DB -> honesto
        logger.info(f"ga4 properties token read failed · {e}")
        return []
    access_token = str(token.get("access_token") or "") if token else ""
    if not access_token:
        return []
    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as http:
            resp = await http.get(_ADMIN_URL, headers={"Authorization": f"Bearer {access_token}"},
                                  params={"pageSize": 200})
    except Exception as e:  # noqa: BLE001
        logger.info(f"ga4 properties call failed · {e}")
        return []
    if resp.status_code != 200:
        logger.info(f"ga4 properties {resp.status_code} · {resp.text[:160]}")
        return []
    out: list[dict[str, str]] = []
    summaries = resp.json().get("accountSummaries")
    for acc in summaries if isinstance(summaries, list) else []:
        props = acc.get("propertySummaries") if isinstance(acc, dict) else None
        for prop in props if isinstance(props, list) else []:
            if not isinstance(prop, dict):
                continue
            raw = str(prop.get("property") or "")
            pid = raw.split("/")[-1] if raw else ""
            if pid:
                out.append({"property_id": pid, "display_name": str(prop.get("displayName") or pid)})
    return out
