"""Load and format ARIA recent memory as system prompt section.

Best-effort: fail-safe a "" en cualquier error (no rompe conversación).
Token-aware: trunca filas hasta caber en max_tokens (~ 4 chars/token).
Llamado desde use_aria_message ANTES de generate() para cerrar el loop P5.
"""
from datetime import datetime, timezone

from app.bc_cognition.infrastructure.aria_memory_repository import (
    fetch_recent_for_owner,
)

_HEADER = "# MEMORIA RECIENTE (últimas interacciones con este cliente)"
_CHARS_PER_TOKEN = 4
_USER_WORDS, _RESP_WORDS = 12, 18


def load_and_format_memory(
    supabase, client_id, reseller_id,
    limit: int = 10, max_tokens: int = 500,
) -> str:
    if not (client_id or reseller_id):
        return ""
    try:
        rows = fetch_recent_for_owner(
            supabase, client_id=client_id, reseller_id=reseller_id, limit=limit,
        )
    except Exception:
        return ""
    return _format(rows, max_tokens) if rows else ""


def _format(rows: list[dict], max_tokens: int) -> str:
    now = datetime.now(timezone.utc)
    budget = max_tokens * _CHARS_PER_TOKEN
    out, used = [_HEADER], len(_HEADER)
    for r in rows:
        line = _format_row(r, now)
        if used + len(line) + 1 > budget:
            break
        out.append(line)
        used += len(line) + 1
    return "\n".join(out) if len(out) > 1 else ""


def _format_row(row: dict, now: datetime) -> str:
    when = _relative_time(row.get("created_at"), now)
    wc = row.get("was_correct")
    flag = "✓" if wc is True else "✗" if wc is False else "?"
    user_msg = _truncate(row.get("context") or "", _USER_WORDS)
    resp = _truncate(row.get("decision") or "", _RESP_WORDS)
    return f'- [{when} · {flag}] Preguntó: "{user_msg}" → Respondiste: "{resp}"'


def _relative_time(value, now: datetime) -> str:
    if not value:
        return "?"
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return "?"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    s = (now - dt).total_seconds()
    if s < 3600:
        return f"hace {int(s // 60)}min"
    if s < 86400:
        return f"hace {int(s // 3600)}h"
    return f"hace {(now - dt).days}d"


def _truncate(text: str, n: int) -> str:
    words = text.split()
    return text if len(words) <= n else " ".join(words[:n]) + "…"
