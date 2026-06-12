"""BUG 3 (11 jun) · extract_draft debe devolver SOLO el copy, no el pre-flight.

Causa real: el modelo antepone un bloque meta ("Voy a ser directo... ## REVIEW
REQUIRED") y devuelve el JSON con el string "draft" envuelto en newlines
LITERALES (JSON inválido para json.loads estricto) → el fallback devolvía el
raw entero (pre-flight incluido) como si fuera el caption. Reproduce primero."""
from app.api.routes.content_lab_v3.handlers._json_extract import extract_draft

# Formato real capturado en prod (draft 1121eb0a · 11 jun): pre-flight meta +
# ```json con el campo "draft" partido por saltos de línea LITERALES + \n escapados.
_LEAK = '''Voy a ser directo antes de generar el output.

---

## REVIEW REQUIRED — Pre-flight check

| Elemento | Problema | Accion |
|---|---|---|
| Insultos | P2 | Reemplazado |

El tono audaz SI lo ejecuto.

---

```json
{
  "draft": "Llevas anios tirando dinero en recogidos de basura
que ni limpian bien.\\n\\nZafacones Ramos lleva 45 anios
arreglando ese problema desde $19.98.",
  "hook": "Llevas anios tirando dinero",
  "framework": "PAS",
  "confidence": 8,
  "review_required": false
}
```
'''


def test_extrae_solo_el_copy_no_el_preflight():
    out = extract_draft(_LEAK)
    assert "REVIEW REQUIRED" not in out
    assert "Voy a ser directo" not in out
    assert out.startswith("Llevas anios tirando dinero")
    assert "Zafacones Ramos lleva 45 anios" in out
    assert "basura que ni limpian bien" in out   # wrap literal colapsado a espacio
    assert "\n\n" in out                          # \n\n intencionales preservados


def test_json_limpio_normal_sigue_funcionando():
    assert extract_draft('{"draft": "Hola mundo", "hook": "Hola"}') == "Hola mundo"


def test_json_en_fence_sigue_funcionando():
    assert extract_draft('```json\n{"draft": "Texto"}\n```') == "Texto"


def test_sin_json_devuelve_raw():
    assert extract_draft("solo texto plano sin json") == "solo texto plano sin json"
