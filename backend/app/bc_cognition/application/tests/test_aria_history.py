"""Tests clean_history · historial siempre válido para Anthropic (fix ARIA silenciosa)."""
from app.bc_cognition.domain.aria_history import clean_history


def _seq(*roles: str) -> list[dict[str, str]]:
    return [{"role": r, "content": f"{r}{i}"} for i, r in enumerate(roles)]


def _valid(h: list[dict[str, str]]) -> bool:
    """Anthropic: empieza en user · alterna (history + [user nuevo] queda válido)."""
    if not h:
        return True
    if h[0]["role"] != "user":
        return False
    return all(h[i]["role"] != h[i - 1]["role"] for i in range(1, len(h)))


def test_happy_three_pairs_ends_assistant():
    out = clean_history(_seq("user", "assistant", "user", "assistant", "user", "assistant"), 5)
    assert _valid(out) and out[-1]["role"] == "assistant"


def test_edge_window_cuts_mid_pair_never_leads_assistant():
    # el bug original: 6 filas, window 5 → antes empezaba con assistant → Anthropic 400
    out = clean_history(_seq("user", "assistant", "user", "assistant", "user", "assistant"), 5)
    assert out and out[0]["role"] == "user"


def test_leading_assistant_dropped():
    assert _valid(clean_history(_seq("assistant", "user", "assistant"), 5))


def test_consecutive_same_role_collapsed():
    # cascada de fallo (user guardado, assistant falló → 2 users seguidos)
    assert _valid(clean_history(_seq("user", "user", "assistant"), 5))


def test_trailing_user_dropped():
    out = clean_history(_seq("user", "assistant", "user"), 5)
    assert not out or out[-1]["role"] == "assistant"


def test_empty():
    assert clean_history([], 5) == []
