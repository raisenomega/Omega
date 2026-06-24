"""Dominio puro · guard de qué texto merece entrar a brand_voice_corpus (A2 · stdlib).

El corpus es la REFERENCIA de voz de marca que el scorer X5 usa como ejemplos
aprobados. Drafts content_type=image guardan la URL de la imagen en generated_text
(no hay caption) → si esa URL entra al corpus, el scorer mide cada caption contra
URLs → score bajo a TODO el negocio (bug confirmado · Zafacones b8d1b9f5). Guard
determinista: solo texto real entra · URLs/vacío fuera. Mejor vacío que basura.
"""

_URL_PREFIXES = ("http://", "https://")


def is_corpus_worthy_text(text: str | None) -> bool:
    """True si `text` es contenido textual real apto como ejemplo de voz de marca.
    False para vacío/whitespace o texto que ARRANCA con una URL (drafts de imagen
    guardan la URL en generated_text · no hay caption que aprender). Una URL DENTRO
    de un caption real no lo descalifica (solo se mira el inicio)."""
    if not text:
        return False
    stripped = text.strip()
    if not stripped:
        return False
    return not stripped.lower().startswith(_URL_PREFIXES)
