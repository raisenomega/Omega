"""Métricas ACUMULADO del panel ampliado (separado del assembler por C4 · puro · cero-sintéticos).

daily-metrics de Zernio NO tiene ventana (date-params ignorados) → todo ACUMULADO, NUNCA "del
período". Empty honesto: None / [] (jamás 0 inventado). total_reach + profile_engagement derivan
de las MISMAS eng_rows (el reach del ER = el de la tabla = el del KPI). Series ← dailyData.
"""
from typing import Any, Dict, List, Optional

from app.api.routes.intelligence._analytics_assembler import _profile_of

# Campos del agregado diario cross-plataforma (dailyData[].metrics · 8 exactos · verificado en vivo).
_SERIE_FIELDS = ("impressions", "reach", "likes", "comments", "shares", "saves", "clicks", "views")
_INTERACTIONS = ("likes", "comments", "shares", "saves")  # ER = interacciones / reach (views NO es interacción)
_NET_COUNTS = ("likes", "comments", "shares", "saves", "views")


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


def _net_series(daily: Dict[str, Any], net: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Series (engagement 8-campos · posts) de UNA red desde dailyData[].platformMetrics[net]."""
    eng: List[Dict[str, Any]] = []
    posts: List[Dict[str, Any]] = []
    for day in daily.get("dailyData", []) or []:
        d = day.get("date")
        m = (day.get("platformMetrics") or {}).get(net)
        if not d or m is None:
            continue
        eng.append({"date": d, **{k: int(m.get(k) or 0) for k in _SERIE_FIELDS}})
        posts.append({"date": d, "count": int(m.get("postCount") or 0)})
    eng.sort(key=lambda r: r["date"])
    posts.sort(key=lambda r: r["date"])
    return eng, posts


def networks_breakdown(daily: Dict[str, Any], accounts: List[Dict[str, Any]],
                       profile_id: str) -> List[Dict[str, Any]]:
    """Vista per-RED del chip · AISLADA por profileId (cero llamada nueva: platformBreakdown + accounts
    + dailyData ya extraídos). Una entrada por cuenta del profile. reach/counts de platformBreakdown,
    followers de la cuenta, ER de ESA red (None si reach=0 → '—', NO 0 disfrazado), series por red."""
    pb = {b.get("platform"): b for b in (daily.get("platformBreakdown") or []) if b.get("platform")}
    out: List[Dict[str, Any]] = []
    for a in accounts:
        net = a.get("platform")
        if _profile_of(a) != profile_id or not net:
            continue
        b = pb.get(net, {})
        counts = {k: int(b.get(k) or 0) for k in _NET_COUNTS}
        reach = int(b.get("reach") or 0)
        inter = sum(counts[k] for k in _INTERACTIONS)
        eng, posts = _net_series(daily, net)
        fc = a.get("followersCount")
        out.append({
            "platform": net,
            "followers": int(fc) if fc is not None else None,
            "reach": reach, **counts,
            "profile_engagement": round(inter / reach * 100, 1) if reach else None,
            "engagement_series": eng,
            "posts_series": posts,
        })
    return sorted(out, key=lambda n: n["platform"])
