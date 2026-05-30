"""Estrategia · domain PURO: arma el system prompt (reusando los bloques ya construidos por el
pipeline de ARIA · NO los reconstruye) y parsea la respuesta de Claude a (titulo, contenido).
Sin I/O · A5 (None si la respuesta no es una estrategia válida)."""
import json
from typing import Optional

_INSTRUCTION = (
    "Sos ARIA preparando una ESTRATEGIA de contenido para este negocio. Con el contexto del "
    "cliente, las tendencias actuales y la memoria, proponé una estrategia accionable para el "
    "periodo. Devolvé SOLO un JSON válido con esta forma exacta (nada de texto fuera del JSON):\n"
    '{"titulo": "<título corto>", "resumen": "<1-2 frases>", '
    '"pilares": ["<pilar 1>", "<pilar 2>", "<pilar 3>"], '
    '"posts_sugeridos": [{"plataforma": "<red>", "idea": "<idea de post>"}]}'
)


def build_strategy_system(ctx_block: str, web_block: str, memory_block: str) -> str:
    """System prompt de estrategia · REUSA los bloques del pipeline de ARIA (no los reconstruye)."""
    return "\n\n".join(p for p in (_INSTRUCTION, ctx_block, web_block, memory_block) if p)


def parse_strategy(text: str) -> Optional[dict]:
    """{titulo, contenido} si el texto trae JSON válido con titulo no vacío; si no → None (A5).
    Tolera ```json ...``` o texto alrededor: toma del primer '{' al último '}'."""
    raw = (text or "").strip()
    a, b = raw.find("{"), raw.rfind("}")
    if a < 0 or b <= a:
        return None
    try:
        data = json.loads(raw[a:b + 1])
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    titulo = str(data.get("titulo") or "").strip()
    if not titulo:
        return None
    return {"titulo": titulo[:200], "contenido": data}
