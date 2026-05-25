"""POST /api/v1/clients/onboarding · Wizard V3 (DEBT-033 mayor close).

DDD A1/A9: handler → repository (NUNCA Supabase directo).
safe_insert envuelve writes secundarios (behavioral_events + agent_memory).
"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3 import _clients_repository as repo
from app.api.routes.clients_v3._onboarding_helpers import calc_completion_percent, validate_payload
from app.api.routes.clients_v3.models.onboarding import OnboardingPayload, OnboardingResponse

router = APIRouter()


def _build_context(p: OnboardingPayload, completion: int) -> dict:
    # tone/primary_goal son list[str] (multi-select) · CSV-join para
    # columnas text en client_context (mismo patrón que identity.regions).
    bv = p.brand_voice.model_dump(exclude={"brand_voice_keywords"})
    bv["tone"] = ",".join(p.brand_voice.tone) if p.brand_voice.tone else None
    g = p.goals.model_dump()
    g["primary_goal"] = ",".join(p.goals.primary_goal) if p.goals.primary_goal else None
    return {
        **p.business.model_dump(),
        **p.audience.model_dump(),
        **bv,
        "brand_voice": {"keywords": p.brand_voice.brand_voice_keywords},
        **g,
        **p.content_history.model_dump(),
        **p.instructions.model_dump(),
        "onboarding_completion_percent": completion,
        "onboarding_complete": completion >= 80,
        "onboarded_at": datetime.now(timezone.utc).isoformat() if completion >= 80 else None,
    }


@router.post("/onboarding", response_model=OnboardingResponse)
async def create_client_onboarding(
    payload: OnboardingPayload,
    authorization: Optional[str] = Header(None),
) -> OnboardingResponse:
    user = await get_current_user(authorization)
    user_id = user["id"]

    ok, err = validate_payload(payload)
    if not ok:
        raise HTTPException(status_code=422, detail=err)

    # REGRESIÓN FIX: clients.reseller_id es NOT NULL → no puede ser null. Resolución por
    # prioridad: reseller propio (si el user es reseller) → reseller de su client existente →
    # reseller default "OMEGA Direct" (cliente directo nuevo, o cuyo client fue borrado · hard-delete).
    reseller_id = (
        repo.resolve_owned_reseller_id(user_id)
        or repo.resolve_reseller_for_user(user_id)
        or repo.get_default_reseller_id()
    )
    if not reseller_id:
        raise HTTPException(status_code=500, detail="default_reseller_missing")

    identity_dict = payload.identity.model_dump()
    regions = identity_dict.pop("regions")
    identity_dict["region"] = ",".join(regions)

    # CRÍTICO: upsert_client genera el ID · si falla el onboarding entero falla
    try:
        client_id = repo.required_insert("upsert_client", repo.upsert_client, user_id, reseller_id, identity_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"upsert_client_failed:{type(e).__name__}:{str(e)[:200]}")

    completion = calc_completion_percent(payload)
    # CRÍTICOS: context + social_accounts + brand_assets + voice_samples
    try:
        repo.required_insert("upsert_client_context", repo.upsert_client_context, client_id, _build_context(payload, completion))
        repo.required_insert("bulk_social", repo.bulk_insert_social_accounts, client_id, [a.model_dump() for a in payload.social_accounts])
        if payload.brand_assets is not None:
            repo.required_insert("brand_assets", repo.upsert_brand_assets, client_id, payload.brand_assets.model_dump())
        repo.required_insert("voice_samples", repo.insert_brand_voice_samples, client_id, payload.brand_voice_samples)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"persist_partial_failed:{type(e).__name__}:{str(e)[:200]}")

    # BEST-EFFORT: telemetría
    repo.safe_insert("behavioral", repo.insert_behavioral_event, user_id, client_id, "client_onboarded",
                     {"completion_percent": completion, "social_accounts": len(payload.social_accounts)})
    repo.safe_insert("memory", repo.insert_agent_memory, user_id, client_id,
                     f"Client onboarded · {payload.identity.industry}/{','.join(payload.identity.regions)}",
                     f"completion={completion}%", 10)

    return OnboardingResponse(client_id=client_id, completion_percent=completion, onboarding_complete=completion >= 80)
