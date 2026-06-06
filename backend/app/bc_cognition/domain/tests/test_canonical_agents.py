from app.bc_cognition.domain import canonical_agents as ca


def test_8_operational():
    assert ca.operational_count() == 8
    ops = {c for c, a in ca.CANONICAL_AGENTS.items() if a["status"] == "operational"}
    assert ops == {"nova_chat", "orchestrator", "content_creator", "strategy",
                   "brand_voice", "analytics", "crisis_manager", "sentinel_security"}


def test_sophia_latent_guardian_subsystem():
    assert ca.CANONICAL_AGENTS["sophia"]["status"] == "latent"
    assert ca.CANONICAL_AGENTS["guardian"]["status"] == "subsystem"


def test_alias_resolution_canonical_targets():
    assert ca.resolve_alias("ATLAS") == "strategy"
    assert ca.resolve_alias("@rafa") == "content_creator"
    assert ca.resolve_alias("ORACLE") == "analytics"
    assert ca.resolve_alias("GUARD") == "guardian"


def test_community_resolves_to_engagement_not_aria():
    for n in ("KIRA", "ECHO", "REVIEW", "NURTURE", "TRIBE", "VOICE", "ANCHOR", "BRIDGE"):
        assert ca.resolve_alias(n) == "engagement"
    assert "aria" not in {v for v in ca.LEGACY_ALIASES.values() if v}


def test_inactive_future_names():
    for n in ("VERA", "LUNA", "REX", "HIRE", "MARGIN", "SCOPE"):
        assert ca.resolve_alias(n) is None
        assert ca.is_inactive_alias(n)


def test_nova_is_opus():
    assert ca.CANONICAL_AGENTS["nova_chat"]["model"] == "claude-opus-4-7"
