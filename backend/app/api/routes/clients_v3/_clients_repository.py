"""Repository clients_v3 · única capa de WRITES Supabase (DDD A1/A9)."""
import asyncio
import logging
from typing import Any, Callable, Optional, ParamSpec, TypeVar
from app.infrastructure.supabase_service import get_supabase_service
from app.bc_cognition.domain.input_threats import redact_pii, InputContext, SanitizerAction
from app.bc_cognition.application.input_sanitizer import sanitize_input
from app.bc_cognition.infrastructure import owner_accounts_repository as owners

logger = logging.getLogger(__name__)
P = ParamSpec("P"); T = TypeVar("T")


async def safe_insert(label: str, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
    """Best-effort wrapper (audit FIX 4 pattern) · errores loguean stack y NO propagan.
    Usar SOLO para writes de telemetría/log (behavioral_events, agent_memory) donde
    el fallo no debe romper la operación principal. Para writes críticos (identidad
    del cliente, context, social_accounts, brand_assets) usar required_insert. DEBT-074: async to_thread."""
    try:
        return await asyncio.to_thread(fn, *args, **kwargs)
    except Exception as e:
        logger.error(f"clients_repository.{label} failed: {e}", exc_info=True)
        return None


def required_insert(label: str, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Critical wrapper · errores loguean stack Y PROPAGAN (caller decide HTTP).
    Usar para writes que el frontend debe saber si fallaron (P1/R5 honestidad).
    Patrón usage en handler:
        try: rows = repo.required_insert('label', repo.fn, *args)
        except Exception as e: raise HTTPException(500, detail=f'op:{type(e).__name__}')
    """
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        logger.error(f"clients_repository.{label} failed: {e}", exc_info=True)
        raise


def _sb() -> Any:
    return get_supabase_service().client


def upsert_client(user_id: str, reseller_id: str, identity: dict[str, str]) -> str:
    existing = _sb().table("clients").select("id").eq("user_id", user_id).limit(1).execute()
    if existing.data:
        _sb().table("clients").update(identity).eq("id", existing.data[0]["id"]).execute()
        return str(existing.data[0]["id"])
    r = _sb().table("clients").insert({**identity, "user_id": user_id, "reseller_id": reseller_id}).execute()
    return str(r.data[0]["id"])


def insert_client(user_id: str, reseller_id: str, identity: dict[str, str]) -> str:
    """SIEMPRE INSERT · cada negocio nuevo = fila nueva (multi-negocio Switcher V1).
    NO upsertea por user_id: eso sobrescribía el 1er negocio al crear el 2º (bug write-side ·
    Mail Boxes Design → Omega Raisen). Editar va por PATCH /clients/{id}/onboarding-data
    con client_id explícito (otro path). upsert_client queda legacy (DEBT-UPSERT-CLIENT-CLEANUP)."""
    row: dict[str, Any] = {**identity, "user_id": user_id, "reseller_id": reseller_id}
    # ARIA dogfood: si el reseller define default_client_aria_level, el cliente nuevo lo HEREDA.
    # NULL (otros resellers · ej. OMEGA Direct) → se omite → DEFAULT del DB (aria_level=1). No afecta a otros.
    lvl = _reseller_default_aria(reseller_id)
    if lvl is not None:
        row["aria_level"] = lvl
    r = _sb().table("clients").insert(row).execute()
    return str(r.data[0]["id"])


def _reseller_default_aria(reseller_id: str) -> Optional[int]:
    """default_client_aria_level del reseller (None si no seteado o error → cae al default del DB)."""
    try:
        r = (_sb().table("resellers").select("default_client_aria_level")
             .eq("id", reseller_id).limit(1).execute())
        return r.data[0].get("default_client_aria_level") if r.data else None
    except Exception:
        return None


def upsert_client_context(client_id: str, context: dict[str, Any]) -> None:
    _sb().table("client_context").upsert({**context, "client_id": client_id}, on_conflict="client_id").execute()


def bulk_insert_social_accounts(client_id: str, accounts: list[dict[str, Any]]) -> None:
    if not accounts: return
    # La columna real del handle es account_name (NO username) · profile_url no existe en
    # el schema → se descartan para no romper el insert (resto de la app ya usa account_name).
    rows = [
        {**{k: v for k, v in a.items() if k not in ("username", "profile_url")},
         "client_id": client_id, "account_name": a.get("username") or ""}
        for a in accounts
    ]
    _sb().table("social_accounts").insert(rows).execute()


def upsert_brand_assets(client_id: str, assets: dict[str, Any]) -> None:
    _sb().table("client_brand_assets").upsert({**assets, "client_id": client_id}, on_conflict="client_id").execute()


def insert_brand_voice_samples(client_id: str, samples: list[str]) -> None:
    # Input Sanitizer (BRAND_CORPUS · spec §6) · descarta samples con injection (T1/T2), usa clean_text.
    rows = []
    for s in samples:
        if not s.strip():
            continue
        si, serr = sanitize_input(s, InputContext.BRAND_CORPUS)
        if serr is not None or si is None or si.action in (SanitizerAction.BLOCK, SanitizerAction.HOLD_FOR_HUMAN_REVIEW):
            logger.warning(f"brand_voice manual_upload descartado (unsafe · {serr.code if serr else si.action.value})")
            continue
        rows.append({"client_id": client_id, "text": si.clean_text, "source": "manual_upload", "tone_tags": []})
    if rows:
        _sb().table("brand_voice_corpus").insert(rows).execute()


def delete_brand_voice_samples_manual(client_id: str) -> None:
    # Replace strategy (igual que social_accounts en update_onboarding_data).
    # Solo borra source='manual_upload' · preserva 'approved_draft' (auto-learn Content Lab).
    _sb().table("brand_voice_corpus").delete().eq("client_id", client_id).eq("source", "manual_upload").execute()


def insert_behavioral_event(user_id: str, client_id: str, event_type: str, event_data: dict) -> None:
    _sb().table("behavioral_events").insert({
        "user_id": user_id, "client_id": client_id, "event_type": event_type, "event_data": event_data,
    }).execute()


def insert_agent_memory(user_id: str, client_id: str, context: str, decision: str, confidence: int) -> None:
    _sb().table("agent_memory").insert({
        "user_id": user_id, "client_id": client_id, "agent_code": "nova", "memory_type": "semantic",
        "context": redact_pii(context)[0], "decision": redact_pii(decision)[0], "confidence": confidence, "was_correct": True,
    }).execute()


def resolve_reseller_for_user(user_id: str) -> Optional[str]:
    r = _sb().table("clients").select("reseller_id").eq("user_id", user_id).limit(1).execute()
    return str(r.data[0]["reseller_id"]) if r.data else None


def resolve_owned_reseller_id(user_id: str) -> Optional[str]:
    """Reseller que el user POSEE (owner_user_id) · para que un reseller cree sus clientes."""
    r = _sb().table("resellers").select("id").eq("owner_user_id", user_id).limit(1).execute()
    return str(r.data[0]["id"]) if r.data else None


def get_default_reseller_id() -> Optional[str]:
    """Reseller default 'OMEGA Direct' (slug omega-direct · migración 00006) · clientes directos.
    clients.reseller_id es NOT NULL → un cliente directo se asigna a este reseller plataforma."""
    r = _sb().table("resellers").select("id").eq("slug", "omega-direct").limit(1).execute()
    return str(r.data[0]["id"]) if r.data else None


def update_client_by_id(client_id: str, fields: dict[str, Any]) -> int:
    """Retorna número de rows actualizadas · 0 si client_id no existe."""
    result = _sb().table("clients").update(fields).eq("id", client_id).execute()
    return len(result.data or [])


def delete_social_accounts(client_id: str) -> None:
    _sb().table("social_accounts").delete().eq("client_id", client_id).execute()


def promote_client_plan_enterprise(client_id: str) -> int:
    """Espejo migr 00075 paso 3 · client_plans = fuente del gate (useClientPlanStatus.plan).
    Enterprise PERPETUO (2099) · NO toca clients.plan ni ownership. Retorna rows actualizadas."""
    res = (_sb().table("client_plans")
           .update({"plan": "enterprise", "current_period_end": "2099-12-31T00:00:00+00:00"})
           .eq("client_id", client_id).execute())
    return len(res.data or [])


def promote_if_owner(user_id: str, client_id: str) -> bool:
    """Cuenta-dueño (owner_accounts · migr 00074) → negocio nuevo nace Enterprise perpetuo.
    Cuenta normal → no-op (default/trial · sin cambio). fail-safe: si la lectura del flag falla,
    fetch_owner_user_ids devuelve set() → no-op (NUNCA abre puerta de más). El flag SOLO decide
    el PLAN: no otorga rol, no cambia scope · ownership intacto. Retorna True si promovió."""
    if user_id not in owners.fetch_owner_user_ids():
        return False
    promote_client_plan_enterprise(client_id)
    return True
