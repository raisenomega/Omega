"""
OmegaRaisen — Guardrails inmutables del dominio.

Este archivo es el equivalente Python de `riskLimits.ts` con `Object.freeze()`
descrito en DDD_REGLAS_OMEGA.md regla G1. Su contenido define límites
hardcoded que NINGÚN componente puede sobrepasar.

REGLAS DE MODIFICACIÓN
======================
1. CAMBIO REQUIERE TEST QUE FALLA PRIMERO
   El test que verifica el nuevo valor debe estar commiteado ANTES
   de modificar este archivo. Sin ese test: PR rechazado.

2. SHA1 ROTATION
   Cualquier cambio aquí rota el SHA1 verificado por
   scripts/verify-guardrails.sh. El nuevo SHA1 debe registrarse en
   scripts/guardrails-sha1.txt en el mismo commit.

3. APROBACIÓN OWNER
   Cambios en este archivo requieren aprobación firmada del owner
   en el PR description (no en commit message).

4. ROLLBACK PLAN
   Cada cambio debe documentar cómo revertir si rompe producción.

VERIFICACIÓN
============
    bash scripts/verify-guardrails.sh
    # Esperado: ✅ SHA1 OK · Object.freeze equivalent activo

USO EN CÓDIGO
=============
    from app.bc_cognition.domain.limits_omega import LIMITS_OMEGA, ACCIONES_PROHIBIDAS

    if confidence < LIMITS_OMEGA["MIN_CONFIDENCE_TO_ACT"]:
        return hold_for_human_review()

    if action.type in ACCIONES_PROHIBIDAS:
        raise PermissionError(f"Action {action.type} hardcoded prohibited")

Última actualización: 17 mayo 2026
SHA1 baseline: ver scripts/guardrails-sha1.txt
"""

from types import MappingProxyType
from typing import Final

# ─────────────────────────────────────────────────────────────────────
# LÍMITES NUMÉRICOS DEL NEGOCIO
# ─────────────────────────────────────────────────────────────────────

_LIMITS_RAW = {
    # Convicción mínima para que un agente actúe autónomamente
    # Escala 0-10. Debajo de este umbral: hold_for_human_review.
    "MIN_CONFIDENCE_TO_ACT": 7,

    # Posts automáticos máximos por día POR RED (anti-spam · no palanca de negocio)
    # Más de esto en UNA red: forzar revisión humana. El freno real es el espaciado de 2h.
    "MAX_POSTS_AUTO_PER_DIA_RED": 24,

    # Gasto máximo automático en ads pagados (USD)
    # Operaciones >$50 requieren aprobación owner.
    "MAX_USD_AUTO_AD_SPEND": 50,

    # Costo máximo diario de API de IA por cliente (USD)
    # Circuit breaker — si se excede, degrada routing a Haiku.
    "MAX_USD_DIARIO_API_POR_CLIENTE": 5,

    # Tokens máximos de contexto dinámico (DDD I6: Lost-in-the-Middle)
    # El context_builder NUNCA produce más que esto.
    "MAX_TOKENS_CONTEXT_DINAMICO": 2000,

    # Horas mínimas entre posts del mismo cliente (anti-spam)
    "MIN_HORAS_ENTRE_POSTS": 2,

    # Latencia máxima aceptable de Claude API antes de circuit-breaker (ms)
    # Excedido: failover a Haiku o queue background.
    "MAX_CLAUDE_LATENCY_MS": 30_000,

    # Tasa máxima de errores consecutivos antes de pausar agente
    "MAX_AGENT_CONSECUTIVE_ERRORS": 5,

    # Días máximos antes de re-evaluar was_correct en agent_memory
    # Si pasan más sin evaluación: bias-detection lo flaggea.
    "MAX_DIAS_SIN_EVALUAR_DECISION": 7,

    # Score mínimo de SENTINEL para permitir deploy a producción
    "MIN_SENTINEL_SCORE_DEPLOY": 95,

    # Versión del esquema de este archivo (incrementa al modificar)
    "SCHEMA_VERSION": 1,
}

# Object.freeze() equivalente en Python: MappingProxyType wraps dict read-only
LIMITS_OMEGA: Final[MappingProxyType] = MappingProxyType(_LIMITS_RAW)


# ─────────────────────────────────────────────────────────────────────
# ACCIONES PROHIBIDAS — frozenset inmutable
# ─────────────────────────────────────────────────────────────────────

ACCIONES_PROHIBIDAS: Final[frozenset[str]] = frozenset({
    # CRISIS — nunca responder públicamente sin firma humana
    "respond_to_complaint_publicly",
    "post_apology_for_crisis",
    "delete_negative_comment",          # P1: cero whitewashing
    "block_user_account_complainant",   # P2: preservar reputación legal

    # PROSPECTING — cero contacto sin consentimiento (CAN-SPAM/GDPR/LGPD)
    "contact_lead_without_consent",
    "scrape_email_from_social",
    "auto_dm_followers",
    "auto_follow_for_engagement_bait",

    # DESTRUCCIÓN DE DATOS — irreversible sin firma humana
    "delete_client_brand_file",
    "delete_agent_memory_entry",
    "truncate_table",
    "drop_index",
    "purge_audit_log",

    # FINANCIERO — contractual con cliente
    "modify_stripe_subscription_amount",
    "cancel_stripe_subscription_for_client",
    "issue_refund_without_approval",
    "transfer_stripe_balance",

    # OAUTH / PUBLICACIÓN
    "auto_post_to_paid_account_no_oauth",
    "post_during_client_pause_window",
    "post_with_competitor_mention",     # requiere aprobación de marca

    # GOBIERNO IA
    "modify_persona_system_prompt",     # X2 — personas inmutables
    "modify_routing_table",             # I2 — routing fijo
    "modify_limits_omega",              # este archivo (recursive guard)
    "modify_guardrails_sha1_baseline",
})


# ─────────────────────────────────────────────────────────────────────
# FACTS VERIFICABLES — para tests
# ─────────────────────────────────────────────────────────────────────

def is_limits_immutable() -> bool:
    """Test helper: verifica que LIMITS_OMEGA no acepta escrituras."""
    try:
        LIMITS_OMEGA["MIN_CONFIDENCE_TO_ACT"] = 0  # type: ignore[index]
        return False
    except TypeError:
        return True


def is_acciones_prohibidas_immutable() -> bool:
    """Test helper: verifica que el set no acepta adición."""
    try:
        ACCIONES_PROHIBIDAS.add("anything")  # type: ignore[attr-defined]
        return False
    except AttributeError:
        return True


def get_limit(key: str) -> int:
    """Acceso seguro a un límite. Lanza KeyError si no existe."""
    return LIMITS_OMEGA[key]


def is_action_prohibited(action_type: str) -> bool:
    """Verifica si una acción está hardcoded como prohibida."""
    return action_type in ACCIONES_PROHIBIDAS


# ─────────────────────────────────────────────────────────────────────
# RAZÓN DE EXISTIR DE CADA LÍMITE (auditoría futura)
# ─────────────────────────────────────────────────────────────────────

_LIMIT_RATIONALES = MappingProxyType({
    "MIN_CONFIDENCE_TO_ACT": (
        "Regla P3 del proyecto: cero acción autónoma sin convicción. "
        "Calibrado con datos de 2026-Q1 — debajo de 7, error rate >40%."
    ),
    "MAX_POSTS_AUTO_PER_DIA_RED": (
        "Anti-spam POR RED, no palanca de negocio. El freno real es el espaciado "
        "de 2h (~12/día físico). 24/red es backstop generoso muy por debajo del "
        "techo técnico de IG (100 posts/24h)."
    ),
    "MAX_USD_AUTO_AD_SPEND": (
        "Pérdida tolerable sin firma humana. >$50 → owner approval "
        "vía NOVA chat alert."
    ),
    "MAX_USD_DIARIO_API_POR_CLIENTE": (
        "Circuit breaker — protege margen del reseller. Si cliente "
        "gasta >$5/día, se degrada Sonnet→Haiku con notificación."
    ),
    "MAX_TOKENS_CONTEXT_DINAMICO": (
        "DDD I6 Lost-in-the-Middle: rendimiento degrada >2k tokens "
        "de contexto dinámico. Lo importante va al inicio y al final."
    ),
    "MIN_HORAS_ENTRE_POSTS": (
        "Anti-spam algorítmico. Plataformas penalizan publicación "
        "ráfaga con throttling de alcance."
    ),
    "MAX_CLAUDE_LATENCY_MS": (
        "UX timeout. >30s sin respuesta = usuario abandona. "
        "Failover a Haiku o background job pattern."
    ),
    "MAX_AGENT_CONSECUTIVE_ERRORS": (
        "Bug en agente o degradación de modelo. Pausa preventiva "
        "evita amplificación del error."
    ),
    "MAX_DIAS_SIN_EVALUAR_DECISION": (
        "Regla P5: aprendizaje honesto requiere evaluar was_correct. "
        "Decisiones sin evaluar pierden valor de entrenamiento."
    ),
    "MIN_SENTINEL_SCORE_DEPLOY": (
        "Regla X1 (OmegaRaisen): SENTINEL es el guardián. Score <95 "
        "indica problema que NO debe llegar a producción."
    ),
    "SCHEMA_VERSION": (
        "Incremento manual al modificar este archivo. Permite a "
        "migrations y código consumidor detectar cambios incompatibles."
    ),
})


def get_rationale(key: str) -> str:
    """Razón documentada de por qué un límite tiene su valor."""
    return _LIMIT_RATIONALES.get(key, "Sin razonamiento documentado.")


# ─────────────────────────────────────────────────────────────────────
# Self-check al importar (fail-fast si algo se rompió)
# ─────────────────────────────────────────────────────────────────────

assert is_limits_immutable(), \
    "❌ LIMITS_OMEGA mutable — Object.freeze equivalente roto"
assert is_acciones_prohibidas_immutable(), \
    "❌ ACCIONES_PROHIBIDAS mutable — frozenset comprometido"
assert LIMITS_OMEGA["MIN_CONFIDENCE_TO_ACT"] >= 7, \
    "❌ MIN_CONFIDENCE_TO_ACT < 7 — viola regla P3"
assert "respond_to_complaint_publicly" in ACCIONES_PROHIBIDAS, \
    "❌ ACCIONES_PROHIBIDAS modificada — falta acción crítica P4"
