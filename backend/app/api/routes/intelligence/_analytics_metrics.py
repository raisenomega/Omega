"""Métricas ACUMULADO del panel ampliado (separado del assembler por C4 · puro · cero-sintéticos).

daily-metrics de Zernio NO tiene ventana (date-params ignorados · ver ESTADO_OMEGA) → todo es
ACUMULADO / todo el registro, NUNCA "del período". Empty honesto: None / [] (jamás 0 inventado).
total_reach + profile_engagement derivan de las MISMAS filas de engagement_by_network (consistencia
interna garantizada: el reach del ER = el reach de la tabla = el del KPI). Series ← dailyData.
"""
from typing import Any, Dict, List, Optional

# Campos del agregado diario cross-plataforma (dailyData[].metrics · 8 exactos · verificado en vivo).
_SERIE_FIELDS = ("impressions", "reach", "likes", "comments", "shares", "saves", "clicks", "views")
_INTERACTIONS = ("likes", "comments", "shares", "saves")  # ER = interacciones / reach (views NO es interacción)


def total_reach(eng_rows: List[Dict[str, Any]]) -> Optional[int]:
    """Σ reach de todas las redes (acumulado). None si no hay filas → la UI muestra '—' (nunca 0 inventado).
    Deriva de engagement_by_network (misma fuente que la tabla y el ER · no se descuadra)."""
    if not eng_rows:
        return None
    return sum(int(r.get("reach") or 0) for r in eng_rows)


def profile_engagement(eng_rows: List[Dict[str, Any]]) -> Optional[float]:
    """Engagement promedio HISTÓRICO = Σ interacciones / Σ reach * 100 (1 decimal). None si reach=0
    (→ '—' honesto · evita div/0 Y el % engañoso con denominador vacío). NUNCA es 'ER' comparable Zernio."""
    reach = sum(int(r.get("reach") or 0) for r in eng_rows)
    if not reach:
        return None
    inter = sum(int(r.get(k) or 0) for r in eng_rows for k in _INTERACTIONS)
    return round(inter / reach * 100, 1)


def engagement_series(daily: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Serie diaria de engagement (8 campos · de dailyData[].metrics · acumulado · ordenada por fecha).
    Días sin fecha se descartan. [] si no hay datos → empty state honesto."""
    out: List[Dict[str, Any]] = []
    for day in daily.get("dailyData", []) or []:
        d = day.get("date")
        if not d:
            continue
        m = day.get("metrics") or {}
        out.append({"date": d, **{k: int(m.get(k) or 0) for k in _SERIE_FIELDS}})
    return sorted(out, key=lambda r: r["date"])


def posts_series(daily: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Publicaciones por día (postCount real de dailyData · acumulado · NO ventana). [] si no hay datos."""
    out: List[Dict[str, Any]] = []
    for day in daily.get("dailyData", []) or []:
        d = day.get("date")
        if not d:
            continue
        out.append({"date": d, "count": int(day.get("postCount") or 0)})
    return sorted(out, key=lambda r: r["date"])
