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
    assert "Regiones: PR" in out
    assert "✅ Cuentas sociales: instagram" in out
    assert "❌ Audiencia: sin datos" in out
    assert "❌ Ejemplos de contenido: sin datos" in out


def test_rich_context_fields():
    """Campos del bloque: competidores · logo (URL/no cargado) · colores · avoided/custom/
    what_* (TASK 1) · website/email (TASK 2) · vacíos NO aparecen (P1 · sin placeholders)."""
    ctx = {
        "competitors": [{"name": "Comp A"}, {"name": "Comp B"}],
        "_logo_url": "https://cdn/logo.png",
        "_brand_assets": {"primary_color": "#FF0000", "secondary_color": "#00FF00"},
        "avoided_topics": "política", "avoided_words": ["barato", "gratis"],
        "custom_instructions": "siempre en tú", "what_worked": "reels", "what_failed": "posts largos",
        "_client": {"name": "X", "industry": "i", "website": "milagrosa.online", "business_email": "hola@m.online"},
    }
    out = build_client_context_block(ctx)
    for exp in ("Competidores: Comp A, Comp B", "Logo: disponible (URL: https://cdn/logo.png)",
                "Colores de marca: #FF0000, #00FF00", "Evitar (temas): política",
                "Evitar (palabras): barato, gratis", "Instrucciones del cliente: siempre en tú",
                "Qué funcionó: reels", "Qué falló: posts largos", "Sitio web: milagrosa.online",
                "Email de contacto: hola@m.online"):
        assert exp in out, exp
    empty = build_client_context_block({})
    assert "Logo: no cargado" in empty and "Evitar" not in empty and "Sitio web" not in empty  # P1


def test_profile_mirror_backend_frontend():
    """Convergencia de los 3 calculadores (wizard=backend=ARIA): identidad sin región = ❌;
    audiencia solo edad = ✅; voz solo preferred_formats = ✅ (espejo de c12ef86)."""
    no_region = build_client_context_block({"_client": {"name": "X", "industry": "i"}})
    assert "❌ Identidad: sin datos" in no_region
    assert "✅ Audiencia" in build_client_context_block({"audience_age_range": "18-30"})
    assert "✅ Voz de marca" in build_client_context_block({"preferred_formats": ["reel"]})
    # business_to_whom cuenta (espejo backend) · vertical NO cuenta como negocio
    assert "✅ Negocio" in build_client_context_block({"business_to_whom": "pymes"})
    assert "❌ Negocio: sin datos" in build_client_context_block({"vertical": "x"})
