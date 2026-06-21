"""Ensamblado PURO de las respuestas de Zernio al shape del panel (testeable · sin I/O · cero fabricación).

growth ← follower-history (IG · serie diaria) · engagement ← daily-metrics (por plataforma) ·
heatmap ← best-time slots · KPIs (total_followers/avg_engagement/posts) ← agregados reales.
Si la entrada viene vacía ({}) → salida vacía honesta (None/[]/0), nunca un número inventado.
"""
from typing import Any, Dict, List, Optional, Tuple

from app.bc_cognition.infrastructure.zernio_analytics_adapter import FOLLOWER_FIELD

_DAY = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]  # day_of_week 0-6 (el heatmap agrupa por hora)


def engagement_rows(daily: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Suma por plataforma de daily-metrics.dailyData[].platformMetrics."""
    agg: Dict[str, Dict[str, int]] = {}
    for day in daily.get("dailyData", []) or []:
        for plat, m in (day.get("platformMetrics") or {}).items():
            a = agg.setdefault(plat, {"likes": 0, "comments": 0, "shares": 0})
            a["likes"] += int(m.get("likes") or 0)
            a["comments"] += int(m.get("comments") or 0)
            a["shares"] += int(m.get("shares") or 0)
    return [{"platform": p, **v} for p, v in sorted(agg.items())]


def heatmap_cells(best: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [{"day": _DAY[int(s.get("day_of_week") or 0) % 7], "hour": int(s.get("hour") or 0),
             "value": float(s.get("avg_engagement") or 0)} for s in (best.get("slots", []) or [])]


def growth_series(ig_histories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Serie de seguidores por fecha (suma de las cuentas IG con follower-history · solo IG por ahora)."""
    by_date: Dict[str, int] = {}
    for h in ig_histories:
        fc = (h.get("metrics") or {}).get("follower_count") or {}
        for pt in fc.get("values", []) or []:
            d = pt.get("date")
            if d:
                by_date[d] = by_date.get(d, 0) + int(pt.get("value") or 0)
    return [{"date": d, "followers": by_date[d]} for d in sorted(by_date)]


def followers_total(per_account: List[Tuple[str, Dict[str, Any]]]) -> Optional[int]:
    """Suma de seguidores ACTUALES por cuenta (campo por plataforma) · None si nada real (cero inventado)."""
    total, seen = 0, False
    for platform, data in per_account:
        node = (data.get("metrics") or {}).get(FOLLOWER_FIELD.get(platform, "follower_count")) or {}
        if "total" in node:
            total += int(node.get("total") or 0)
            seen = True
    return total if seen else None


def avg_engagement(daily: Dict[str, Any]) -> Optional[float]:
    """Tasa simple (likes+comments+shares)/impressions*100 · None si sin impresiones (no finge 0%)."""
    inter = imp = 0
    for day in daily.get("dailyData", []) or []:
        m = day.get("metrics") or {}
        inter += int(m.get("likes") or 0) + int(m.get("comments") or 0) + int(m.get("shares") or 0)
        imp += int(m.get("impressions") or 0)
    return round(inter / imp * 100, 1) if imp else None


def posts_count(daily: Dict[str, Any]) -> int:
    return sum(int(d.get("postCount") or 0) for d in (daily.get("dailyData", []) or []))
