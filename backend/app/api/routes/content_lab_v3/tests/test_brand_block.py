"""Pieza 1 · A6 · enchufe de marca (eslabón 4): el prompt de imagen inyecta la paleta del cliente.
_brand_block construye instrucción visual instructiva ("use #X as primary...") solo con los colores
que EXISTEN · _enhance_prompt la concatena. Sin paleta → prompt byte-idéntico a hoy (retrocompat dura).
El hex en DB está limpio (#rrggbb · picker + regex zod) → A6 NO normaliza. G9 exime tests."""
from app.api.routes.content_lab_v3.handlers.generate_image import _brand_block, _enhance_prompt


def test_marca_presente_inyecta_colores():
    """Cliente con paleta completa → los 3 hex aparecen en el prompt final que iría al adapter."""
    block = _brand_block({"primary_color": "#ec1313", "secondary_color": "#7c7979", "accent_color": "#0a0a0a"})
    out = _enhance_prompt("un gato", "realistic", block)
    assert "#ec1313" in out and "#7c7979" in out and "#0a0a0a" in out


def test_sin_marca_prompt_identico():
    """Cliente SIN paleta ({} → block "") → prompt BYTE-idéntico al de hoy (retrocompat dura)."""
    assert _brand_block({}) == ""
    assert _enhance_prompt("un gato", "realistic", _brand_block({})) == _enhance_prompt("un gato", "realistic")


def test_accent_null_se_omite():
    """primary+secondary presentes, accent None → ambos en el prompt, NUNCA 'None' ni basura."""
    out = _enhance_prompt("logo", "minimal", _brand_block({"primary_color": "#0a0557", "secondary_color": "#dfc207", "accent_color": None}))
    assert "#0a0557" in out and "#dfc207" in out
    assert "None" not in out


def test_solo_primary():
    """Solo primary (resto None) → inyecta solo primary, sin romper ni meter basura."""
    out = _enhance_prompt("paisaje", "realistic", _brand_block({"primary_color": "#54ff52"}))
    assert "#54ff52" in out and "None" not in out
