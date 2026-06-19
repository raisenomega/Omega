"""B-2 FB headless · stash IN-MEMORY de los tokens pendientes del select_page (tempToken + connect_token).
SERVER-SIDE ONLY: los tokens NUNCA van al navegador. Keyed por (client_id, platform) — la MISMA key que el
endpoint pending-pages (paso 3, request distinta con JWT) puede derivar del usuario autenticado (el frontend
NO tiene el state firmado efímero). TTL ~15min (vida del tempToken de Zernio) + evicción de expirados.

DEBT-FB-STASH-MULTIWORKER: el stash in-memory asume Railway `--workers 1` (igual que DEBT-SCHEDULER-SPLIT ·
un solo proceso comparte memoria). Multi-worker rompería esto (un worker stashea, otro atiende el fetch).
Alternativa cuando se escale: fila DB efímera. NO construir con DB ahora (sobre-ingeniería para 1 worker)."""
import time
from typing import Optional

_TTL = 900.0  # 15 min · vida del tempToken de Zernio
_store: dict[str, tuple[str, str, float]] = {}   # key → (temp_token, connect_token, expires_at)


def _key(user_id: str, client_id: str, platform: str) -> str:
    return f"{user_id}:{client_id}:{platform}"


def _evict(now: float) -> None:
    for k in [k for k, (_, _, exp) in _store.items() if now >= exp]:
        _store.pop(k, None)


def stash_pending(user_id: str, client_id: str, platform: str, temp_token: str, connect_token: str) -> None:
    """Guarda los tokens server-side keyed por (user_id, client_id, platform) · limpia expirados de paso.
    El user_id (firmado en el state) ata el stash a quien inicio el flujo: el paso 3 exige que el user_id
    del JWT coincida → defensa-en-profundidad (no depende solo del user_owns_client del endpoint)."""
    now = time.time()
    _store[_key(user_id, client_id, platform)] = (temp_token, connect_token, now + _TTL)
    _evict(now)


def get_pending(user_id: str, client_id: str, platform: str) -> Optional[tuple[str, str]]:
    """(temp_token, connect_token) si hay stash VIVO para (user_id, client_id, platform); None si exp/ausente."""
    entry = _store.get(_key(user_id, client_id, platform))
    if not entry:
        return None
    temp, connect, exp = entry
    if time.time() >= exp:
        _store.pop(_key(user_id, client_id, platform), None)
        return None
    return temp, connect


def clear_pending(user_id: str, client_id: str, platform: str) -> None:
    """Borra el stash tras completar el select (exitoso o 403) · higiene de credenciales."""
    _store.pop(_key(user_id, client_id, platform), None)
