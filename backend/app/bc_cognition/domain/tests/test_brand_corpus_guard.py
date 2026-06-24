"""Tests · guard puro de qué texto merece entrar a brand_voice_corpus.

Raíz del bug de score bajo a todo: drafts content_type=image guardan la URL de
la imagen en generated_text (no hay caption) → al aprobar, la URL entraba al
corpus → el scorer X5 medía captions contra URLs → score bajo a TODO el negocio.
El guard rechaza URLs y texto vacío de forma determinista (mejor vacío que basura).
"""
from app.bc_cognition.domain.brand_corpus_guard import is_corpus_worthy_text


def test_image_url_rejected_https() -> None:
    url = "https://rwlnihoqhxwpbehibgxu.supabase.co/storage/v1/object/public/generated-images/x.png"
    assert is_corpus_worthy_text(url) is False


def test_image_url_rejected_http() -> None:
    assert is_corpus_worthy_text("http://example.com/img.jpg") is False


def test_url_with_leading_whitespace_rejected() -> None:
    assert is_corpus_worthy_text("   https://x.co/a.png  ") is False


def test_empty_and_whitespace_rejected() -> None:
    assert is_corpus_worthy_text("") is False
    assert is_corpus_worthy_text("   \n\t ") is False
    assert is_corpus_worthy_text(None) is False


def test_real_caption_accepted() -> None:
    cap = "¿Tu zafacón huele mal? En Zafacones Ramos lo limpiamos y desinfectamos."
    assert is_corpus_worthy_text(cap) is True


def test_caption_containing_url_midtext_accepted() -> None:
    # Una URL DENTRO de un caption real no lo descalifica (solo URL al inicio).
    cap = "Mirá nuestro antes/después acá: https://zafacones.com/galeria · ¡Reservá hoy!"
    assert is_corpus_worthy_text(cap) is True
