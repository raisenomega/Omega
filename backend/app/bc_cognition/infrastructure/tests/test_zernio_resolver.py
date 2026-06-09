"""zernio_resolver · binding determinístico per-negocio (post-INCIDENTE fuga multi-tenant 8 jun). G9 exime.
El fallback 2a 'en vivo' (usar la unica cuenta del workspace cuando mapped=None) fue ELIMINADO: publicaba
el contenido de cualquier negocio en la unica cuenta IG (caso real: Mail Boxes Design -> @raisenagency).
Ahora: solo binding per-negocio (mapped_account_id) · sin binding -> falla honesto (NO adivina)."""
import asyncio

import pytest

from app.bc_cognition.infrastructure import zernio_resolver as zr


def test_binding_per_negocio_gana():
    # mapped = zernio_account_id del negocio activo → se usa tal cual (cero consulta a Zernio).
    assert asyncio.run(zr.resolve_account_id("instagram", "IG_DEL_NEGOCIO")) == "IG_DEL_NEGOCIO"


def test_sin_binding_falla_honesto_no_adivina():
    # mapped=None → NO fallback a 'la unica cuenta del workspace' (cierra la fuga) → falla honesto.
    with pytest.raises(zr.ZernioAccountResolutionError) as ei:
        asyncio.run(zr.resolve_account_id("instagram", None))
    assert "zernio_sin_cuenta:instagram" in str(ei.value)


def test_binding_vacio_tambien_falla():
    with pytest.raises(zr.ZernioAccountResolutionError):
        asyncio.run(zr.resolve_account_id("facebook", ""))
