"""Limpieza del historial de ARIA para la API de Anthropic (dominio puro · A2).

Anthropic exige que `messages` empiece con role='user' y ALTERNE user/assistant.
`clean_history` toma filas crudas (mezcla user/assistant · cronológicas asc) y devuelve
una secuencia válida: empieza en user · alterna · termina en assistant (para que
`history + [user nuevo]` siga alternando). Sin esto, una ventana que cortaba a mitad de
un par dejaba un 'assistant' líder → Anthropic 400 → ARIA silenciosa desde el 4º mensaje.
"""


def clean_history(rows: list[dict[str, str]], window: int) -> list[dict[str, str]]:
    """rows: cronológico asc {role, content}. Devuelve ≤window msgs · válido para Anthropic."""
    alt: list[dict[str, str]] = []
    for m in rows:
        if not alt:
            if m["role"] == "user":
                alt.append(m)  # arranca en el primer user (drop assistants líderes)
        elif m["role"] != alt[-1]["role"]:
            alt.append(m)  # alterna → agregar
        else:
            alt[-1] = m  # consecutivo del mismo rol → quedarse con el más reciente
    trimmed = alt[-window:]
    if trimmed and trimmed[0]["role"] != "user":
        trimmed = trimmed[1:]  # el trim pudo re-dejar un assistant líder
    if trimmed and trimmed[-1]["role"] == "user":
        trimmed = trimmed[:-1]  # terminar en assistant (history + [user nuevo] alterna)
    return trimmed
