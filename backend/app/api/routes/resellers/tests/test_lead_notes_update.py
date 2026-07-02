"""update_lead_status extendido: status y/o notes opcionales. Verifica que guardar SOLO notas no
toca status ni resetea contacted_at (bug del path acoplado), que notes='' limpia, y el no-op."""
import asyncio
from types import SimpleNamespace

from app.infrastructure.supabase_leads_mixin import LeadsMixin


class _Tbl:
    def __init__(self, cap):
        self.cap = cap
    def update(self, data):
        self.cap["update"] = data
        return self
    def eq(self, *a):
        return self
    def execute(self):
        return SimpleNamespace(data=[{"id": "l1", **self.cap.get("update", {})}])


class _Mix(LeadsMixin):
    def __init__(self, cap, existing):
        self.client = SimpleNamespace(table=lambda n: _Tbl(cap))
        self._existing = existing
    async def get_lead_by_id(self, lead_id):
        return self._existing


def test_notes_only_no_toca_status_ni_contacted_at():
    cap: dict = {}
    m = _Mix(cap, {"id": "l1", "status": "contacted", "contacted_at": "2026-01-01T00:00:00Z"})
    asyncio.run(m.update_lead_status("l1", status=None, notes="llamé al cliente"))
    assert cap["update"] == {"notes": "llamé al cliente"}  # NO status, NO contacted_at reset


def test_notes_vacio_limpia():
    cap: dict = {}
    m = _Mix(cap, {})
    asyncio.run(m.update_lead_status("l1", status=None, notes=""))
    assert cap["update"] == {"notes": ""}


def test_status_contacted_setea_contacted_at():
    cap: dict = {}
    m = _Mix(cap, {})
    asyncio.run(m.update_lead_status("l1", status="contacted"))
    assert cap["update"]["status"] == "contacted"
    assert "contacted_at" in cap["update"]


def test_noop_devuelve_lead_actual_sin_update():
    cap: dict = {}
    existing = {"id": "l1", "status": "new"}
    m = _Mix(cap, existing)
    out = asyncio.run(m.update_lead_status("l1", status=None, notes=None))
    assert out == existing
    assert "update" not in cap  # no llamó a .update()
