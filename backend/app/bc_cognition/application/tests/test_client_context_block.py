"""Tests client_context_block · contexto ampliado de ARIA (TAREA C). 4 casos."""
from app.bc_cognition.domain.client_context_block import build_client_context_block


def test_happy_full_context_all_fields():
    """Todos los campos + cuentas → aparecen en el bloque."""
    ctx = {
        "niche": "cafetería", "business_diff": "tueste propio",
        "target_audience": "jóvenes", "audience_age_range": "18-30", "audience_gender": "mixed",
        "primary_goal": "leads,sales", "goal_this_month": "50 seguidores",
        "tone": "casual,divertido", "emoji_usage": "moderate", "hashtag_strategy": "nicho",
        "social_accounts": [{"platform": "instagram", "account_name": "milcafe"}],
    }
    out = build_client_context_block(ctx)
    assert "Negocio: cafetería" in out and "Diferenciador: tueste propio" in out
    assert "Audiencia: jóvenes · 18-30 · mixed" in out
    assert "Objetivos: leads, sales · 50 seguidores" in out
    assert "Voz de marca: casual, divertido · moderate · nicho" in out
    assert "instagram @milcafe" in out


def test_edge_no_accounts_says_ninguna():
    """Sin cuentas → ARIA sabe que NO tiene (no inventa)."""
    out = build_client_context_block({"niche": "x", "social_accounts": []})
    assert "Cuentas conectadas: ninguna aún." in out


def test_boundary_caps():
    """uploaded capado a 1500 + bloque total nunca excede 2000 (I6)."""
    out = build_client_context_block({"niche": "x", "uploaded_context_text": "z" * 5000})
    assert len(out) <= 2000
    assert ("z" * 1500) in out and ("z" * 1501) not in out


def test_error_empty_ctx_still_has_accounts_line():
    """ctx vacío → bloque mínimo con header + perfil 0/10 (nunca crashea)."""
    out = build_client_context_block({})
    assert "CONTEXTO DEL CLIENTE" in out and "ninguna aún" in out
    assert "Perfil completado: 0/10 secciones." in out


def test_profile_completion_counts_and_lists():
    """X/10 correcto + ✅ con detalle / ❌ sin datos por sección (ARIA guía qué falta)."""
    ctx = {
        "_client": {"name": "La Milagrosa", "industry": "inmobiliaria", "region": "PR"},
        "niche": "bienes raíces",
        "social_accounts": [{"platform": "instagram", "account_name": "milcasa"}],
        "_brand_assets": {}, "_samples_count": 0,
    }
    out = build_client_context_block(ctx)
    assert "Perfil completado: 3/10 secciones." in out
    assert "✅ Identidad: La Milagrosa" in out
    assert "✅ Negocio: bienes raíces" in out
    assert "✅ Cuentas sociales: instagram" in out
    assert "❌ Audiencia: sin datos" in out
    assert "❌ Ejemplos de contenido: sin datos" in out


def test_profile_mirror_frontend_edge_cases():
    """Espejo estricto del wizard (guardian): identidad sin región = ❌ · audiencia solo edad = ❌."""
    no_region = build_client_context_block({"_client": {"name": "X", "industry": "i"}})
    assert "❌ Identidad: sin datos" in no_region
    age_only = build_client_context_block({"audience_age_range": "18-30"})
    assert "❌ Audiencia: sin datos" in age_only
