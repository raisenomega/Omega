"""Pieza 1 · A7 · round-trip ratio↔size: que 4:5 (y los demás) NO caigan silencioso a 1:1.
El handler mapea ratio→size (_ASPECT_TO_SIZE) y _image_compat lo devuelve size→ratio (_SIZE_TO_ASPECT).
Si falta el 4:5 en CUALQUIERA de los dos mapas, el adapter recibe '1:1' (cuadrado) en vez de '4:5' (vertical).
G9 exime tests."""
import pytest

from app.api.routes.content_lab_v3.handlers.generate_image import _ASPECT_TO_SIZE
from app.bc_cognition.infrastructure._image_compat import _SIZE_TO_ASPECT


def _round_trip(aspect: str) -> str:
    """Simula el camino real: ratio → size (handler · default 1024x1024) → ratio (compat · default 1:1).
    Si algún mapa no tiene la entrada → cae al default → el adapter recibe ese default, no el ratio pedido."""
    size = _ASPECT_TO_SIZE.get(aspect, "1024x1024")
    return _SIZE_TO_ASPECT.get(size, "1:1")


def test_4x5_round_trip():
    """4:5 entra → llega '4:5' al adapter (NO '1:1' silencioso). Fija que AMBOS mapas tienen la entrada."""
    assert _round_trip("4:5") == "4:5"


@pytest.mark.parametrize("aspect", ["1:1", "9:16", "16:9"])
def test_ratios_existentes_intactos(aspect):
    """Additive no rompió los ratios de hoy: cada uno round-trippea a sí mismo."""
    assert _round_trip(aspect) == aspect
