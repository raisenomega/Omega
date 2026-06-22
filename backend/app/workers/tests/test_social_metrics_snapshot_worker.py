"""Worker snapshot · best-effort por negocio + wiring + today inyectable. Sin DB (mocks)."""
import asyncio
import importlib

w = importlib.import_module("app.workers.social_metrics_snapshot_worker")


def _wire(monkeypatch, profiles, daily_for, accounts=None):
    monkeypatch.setattr(w.repo, "fetch_active_profiles", lambda: profiles)
    async def _accs(): return accounts or []
    monkeypatch.setattr(w.za, "list_accounts", _accs)
    async def _daily(pid): return daily_for(pid)   # puede levantar para simular fallo
    monkeypatch.setattr(w.za, "daily_metrics", _daily)
    captured = []
    monkeypatch.setattr(w.repo, "upsert_social_metrics", lambda rows: captured.append(rows) or len(rows))
    return captured


def test_best_effort_un_fallo_no_tumba_la_corrida(monkeypatch):
    """p2 falla en Zernio → p1 igual se guarda · la corrida termina (no crashea)."""
    profiles = [{"client_id": "c1", "profile_id": "p1"}, {"client_id": "c2", "profile_id": "p2"}]
    accs = [{"_id": "ig", "platform": "instagram", "profileId": "p1", "followersCount": 10}]
    def daily_for(pid):
        if pid == "p2":
            raise RuntimeError("zernio down for p2")
        return {"dailyData": []}
    cap = _wire(monkeypatch, profiles, daily_for, accs)
    out = asyncio.run(w.run(today="2026-06-22"))
    assert out == {"profiles": 2, "rows": 1}           # p1 (1 fila followers) · p2 saltado
    assert cap and cap[0][0]["client_id"] == "c1"      # se guardó la de c1
    assert all(r["client_id"] != "c2" for batch in cap for r in batch)  # c2 NO escribió basura


def test_sin_negocios_no_hace_nada(monkeypatch):
    _wire(monkeypatch, [], lambda pid: {})
    assert asyncio.run(w.run(today="2026-06-22")) == {"profiles": 0, "rows": 0}


def test_today_inyectable_va_a_la_fila(monkeypatch):
    """El snapshot de followers usa el `today` dado (determinista · DEBT-HERMES-CRON-TEST-TIME)."""
    profiles = [{"client_id": "c1", "profile_id": "p1"}]
    accs = [{"_id": "ig", "platform": "instagram", "profileId": "p1", "followersCount": 5}]
    cap = _wire(monkeypatch, profiles, lambda pid: {"dailyData": []}, accs)
    asyncio.run(w.run(today="2026-01-15"))
    assert cap[0][0]["metric_date"] == "2026-01-15" and cap[0][0]["followers"] == 5
