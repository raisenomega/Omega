"""Commit 5b · puntúa el guion del carrusel al GENERAR (paridad con el caption · _variations.py:85,110).
Reusa EXACTAMENTE el scorer del caption (build_dna_for_client + compute_virality_score) · NO duplica lógica.

Best-effort: si el scoring falla (DNA/virality), devuelve (0, 0.0) → el carrusel se devuelve igual sin chips
(mejor un carrusel sin chips que un 500 · la generación ya pasó). vertical=None: solo afecta el fallback de
corpus vacío (donde dna.score=0 igual) · para clientes con corpus real devuelve el DNA persistido."""
import logging

from app.bc_cognition.application import use_brand_dna
from app.bc_cognition.domain.virality_score import compute_virality_score

logger = logging.getLogger(__name__)

_CAROUSEL_PLATFORM = "instagram"  # el carrusel es feed/IG · el request no trae platform


def build_guion_text(title: str, slides: list) -> str:
    """Texto evaluable del carrusel = título + el copy de cada placa (mismo criterio que el gate de marca)."""
    parts = [t for t in [(title or "").strip()] if t]
    for s in slides or []:
        txt = (getattr(s, "text", "") or "").strip()
        if txt:
            parts.append(txt)
    return "\n\n".join(parts)


def score_guion(client_id: str, title: str, slides: list) -> tuple[int, float]:
    """(virality_score, brand_dna_score) del guion · best-effort: fallo → (0, 0.0), NO rompe el render."""
    try:
        dna = use_brand_dna.build_dna_for_client(client_id)  # vertical=None · solo afecta fallback corpus-vacío
        virality = compute_virality_score(build_guion_text(title, slides), dna, _CAROUSEL_PLATFORM)
        return int(virality["score"]), float(dna.score)
    except Exception as e:  # noqa: BLE001 · best-effort · mejor carrusel sin chips que 500
        logger.warning(f"carousel scoring falló · sin chips · client={client_id}: {e}")
        return 0, 0.0
