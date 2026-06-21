"""Ensamblado PURO de Zernio → shape del panel (testeable · sin I/O · regla GLOBAL cero-sintéticos).

followers ← /accounts.followersCount (snapshot · SOLO bound_ids del negocio · NUNCA page_follows) ·
posts ← /accounts.externalPostCount (conteo real) · best_hour ← slot de mayor avg_engagement (derivado) ·
engagement ← daily-metrics por plataforma (likes/comments/shares/saves/views del período) ·
growth ← follower-history IG (serie). SIN porcentajes. Entrada vacía → salida vacía honesta (None/[]/0).
"""
from typing import Any, Dict, List, Optional

_DAY = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]  # day_of_week 0-6 (el heatmap agrupa por hora)
_NET_FIELDS = ("likes", "comments", "shares", "saves", "views")


def followers_total(accounts_api: List[Dict[str, Any]], bound_ids: List[str]) -> Optional[int]:
    """Σ followersCount SOLO de las cuentas del negocio (bound_ids). None si ninguna resuelve.
    NUNCA toca page_follows (suma de ventana · raíz del 28)."""
    bset, total, seen = set(bound_ids), 0, False
    for a in accounts_api:
        if a.get("_id") in bset and "followersCount" in a:
            total += int(a.get("followersCount") or 0)
            seen = True
    return total if seen else None


def posts_total(accounts_api: List[Dict[str, Any]], bound_ids: List[str]) -> int:
    """Σ externalPostCount (posts reales) de las cuentas del negocio. Total histórico (NO del período)."""
    bset = set(bound_ids)
    return sum(int(a.get("externalPostCount") or 0) for a in accounts_api if a.get("_id") in bset)


def best_hour(best: Dict[str, Any]) -> Optional[str]:
    """Hora real del slot de mayor avg_engagement → 'HH:00' (derivado · NO hardcode). None si sin slots."""
    slots = best.get("slots", []) or []
    if not slots:
        return None
    top = max(slots, key=lambda s: s.get("avg_engagement") or 0)
    return f"{int(top.get('hour') or 0):02d}:00"


def engagement_by_network(daily: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Por plataforma Σ {likes,comments,shares,saves,views} del período (conteos reales · sin %)."""
    agg: Dict[str, Dict[str, int]] = {}
    for day in daily.get("dailyData", []) or []:
        for plat, m in (day.get("platformMetrics") or {}).items():
            a = agg.setdefault(plat, {k: 0 for k in _NET_FIELDS})
            for k in _NET_FIELDS:
                a[k] += int(m.get(k) or 0)
    return [{"platform": p, **v} for p, v in sorted(agg.items())]


def growth_series(ig_histories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Serie de seguidores por fecha (suma de las cuentas IG con follower-history · último = 'ahora')."""
    by_date: Dict[str, int] = {}
    for h in ig_histories:
        fc = (h.get("metrics") or {}).get("follower_count") or {}
        for pt in fc.get("values", []) or []:
            d = pt.get("date")
            if d:
                by_date[d] = by_date.get(d, 0) + int(pt.get("value") or 0)
    return [{"date": d, "followers": by_date[d]} for d in sorted(by_date)]


def heatmap_cells(best: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [{"day": _DAY[int(s.get("day_of_week") or 0) % 7], "hour": int(s.get("hour") or 0),
             "value": float(s.get("avg_engagement") or 0)} for s in (best.get("slots", []) or [])]
