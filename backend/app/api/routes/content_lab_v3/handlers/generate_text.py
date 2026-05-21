"""POST /api/v1/content-lab/generate · genera texto via anthropic_adapter.

DDD A1/A9: handler -> repo + anthropic_adapter (ÚNICO entry I1).
Routing: agent_code='content_creator' -> Sonnet 4.6 (I2).
Insert con status='draft' · compliance_passed=True · confidence=8.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3.models.content_lab_models import GenerateTextRequest, GenerateTextResponse
from app.bc_cognition.infrastructure.anthropic_adapter import generate

router = APIRouter()

UI_TO_DB_TYPE = {"caption": "text", "hashtags": "text", "video_script": "video"}


def _build_system(client: dict, ctx: dict, platform: str, content_type: str, tone: str) -> str:
    name = client.get("name") or "este cliente"
    industry = client.get("industry") or "su industria"
    audience = ctx.get("target_audience") or client.get("target_audience") or "su audiencia"
    bv = ctx.get("brand_voice") or client.get("brand_voice") or {}
    keywords = ", ".join(bv.get("keywords", []) if isinstance(bv, dict) else [])
    kw_line = f"Keywords de marca: {keywords}" if keywords else ""
    return (
        f"Eres ARIA, asistente de marketing para {name} ({industry}).\n"
        f"Audiencia: {audience}. Tono: {tone}. Plataforma: {platform}.\n"
        f"{kw_line}\n"
        f"Genera {content_type} optimizado para la plataforma. Breve, en voz del cliente, con CTA claro. "
        f"Sin emojis excesivos. Sin promesas falsas. Sin datos inventados (P1)."
    )


@router.post("/generate", response_model=GenerateTextResponse)
async def generate_text(
    request: GenerateTextRequest,
    authorization: Optional[str] = Header(None),
) -> GenerateTextResponse:
    user = await get_current_user(authorization)
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    client_id = str(client["id"])
    ctx = repo.find_client_context(client_id)
    system = _build_system(client, ctx, request.platform, request.content_type, request.tone)
    messages = [{"role": "user", "content": f"Tema: {request.topic}"}]

    resp, err = await generate(agent_code="content_creator", system=system, messages=messages, max_tokens=600, temperature=0.7)
    if err is not None or resp is None:
        raise HTTPException(status_code=503, detail=f"claude_error:{err.code if err else 'unknown'}")

    db_type = UI_TO_DB_TYPE.get(request.content_type, "text")
    content_id = repo.safe_insert("insert_generated", repo.insert_generated_content, client_id, {
        "agent_code": "content_creator", "content_type": db_type,
        "prompt": request.topic, "generated_text": resp.text,
        "metadata": {"model": resp.model_used, "tokens": resp.input_tokens + resp.output_tokens,
                     "cost_usd": resp.cost_usd, "ui_type": request.content_type,
                     "platform": request.platform, "tone": request.tone},
        "confidence": 8, "status": "draft", "compliance_passed": True,
    })
    return GenerateTextResponse(id=content_id or "", content_type=request.content_type, generated_text=resp.text)
