"""Builder PURO Zernio → filas de social_metrics (testeable · sin I/O · cero-sintéticos).

P1 DURO (el almacén alimenta a LUAN para gastar plata): REAL o None, NUNCA 0 fabricado. Una fila
existe solo si Zernio reportó ALGO para esa (red, fecha) — followers (snapshot de hoy) o actividad
(día real de dailyData). Sin dato → fila ausente / columna None. Un 0 que Zernio SÍ reportó es dato
real y se guarda; la ausencia es None. Cada fila lleva su client_id (aislamiento · no se cruza).
"""
from typing import Any, Dict, List, Optional

# Columna social_metrics ← key de Zernio platformMetrics.
_ACTIVITY = [("reach", "reach"), ("impressions", "impressions"), ("likes", "likes"),
             ("comments", "comments"), ("shares", "shares"), ("saves", "saves"),
             ("views", "views"), ("post_count", "postCount")]


def _profile_of(account: Dict[str, Any]) -> Optional[str]:
    """profileId del account (objeto {_id} o plano) · espejo de _analytics_assembler._profile_of."""
    p = account.get("profileId")
    if isinstance(p, dict):
        return str(p.get("_id")) if p.get("_id") else None
    return str(p) if p else None


def build_snapshot_rows(daily: Dict[str, Any], accounts: List[Dict[str, Any]],
                        client_id: str, profile_id: str, today: str) -> List[Dict[str, Any]]:
    """Filas honestas para upsert. `today` = ISO date del snapshot de followers. Real o None."""
    rows: Dict[tuple, Dict[str, Any]] = {}

    def _row(platform: str, date: str) -> Dict[str, Any]:
        return rows.setdefault((platform, date), {
            "client_id": client_id, "profile_id": profile_id,
            "platform": platform, "metric_date": date,
            "followers": None, "reach": None, "impressions": None, "likes": None,
            "comments": None, "shares": None, "saves": None, "views": None, "post_count": None,
        })

    # Followers = snapshot de HOY · solo redes del profile · solo si Zernio dio el número (None si no).
    for a in accounts:
        net = a.get("platform")
        fc = a.get("followersCount")
        if _profile_of(a) == profile_id and net and fc is not None:
            _row(net, today)["followers"] = int(fc)

    # Actividad = per-día real de dailyData[].platformMetrics[net] · 0-real se guarda, ausente = None.
    for day in daily.get("dailyData", []) or []:
        d = day.get("date")
        if not d:
            continue
        for net, m in (day.get("platformMetrics") or {}).items():
            r = _row(net, d)
            for col, key in _ACTIVITY:
                if m.get(key) is not None:
                    r[col] = int(m[key])
    return list(rows.values())
