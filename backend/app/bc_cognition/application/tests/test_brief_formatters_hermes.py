"""format_sentinel · sección HERMES del brief diario (honesto · nivel 1). G9 exime tests."""
from app.bc_cognition.application._brief_formatters import format_sentinel


def _base(**over):
    r = {"security_score": 90, "status": "ok", "issues": [], "total_issues": 0,
         "critical_issues": 0, "agents_scanned": 8, "deploy_decision": "APPROVE"}
    r.update(over)
    return r


def test_brief_sin_fallos_dice_sin_fallos():
    # Sin hermes_failures → "HERMES: sin fallos" (honesto · NO omite la sección ni inventa).
    _, body = format_sentinel(_base())
    assert "HERMES: sin fallos" in body


def test_brief_con_fallos_lista_las_ventanas():
    _, body = format_sentinel(_base(hermes_failures=[
        {"integration": "zernio", "windows": 3}, {"integration": "resend", "windows": 1}]))
    assert "HERMES · ultimas 24h: zernio (3), resend (1)" in body
