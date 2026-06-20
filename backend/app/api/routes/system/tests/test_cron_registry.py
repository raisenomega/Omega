"""P1-5 · el inventario de crons de main.py == cron_registry (fuente única).

Si alguien agrega/quita un scheduler.add_job sin actualizar cron_registry, este
test falla en CI (cierra el drift documental de DDD X3). Parsea main.py como
texto (no arranca el scheduler · igual que test_nixpacks_workers)."""
import re
from pathlib import Path

from app.workers.cron_registry import CRON_JOB_IDS, EXPECTED_CRON_JOBS

_MAIN = Path(__file__).resolve().parents[4] / "main.py"


def _main_job_ids() -> set:
    text = _MAIN.read_text(encoding="utf-8")
    # add_job( ... id='x' )  · cualquier comilla · incluye dígitos · NO add_jobstore
    return set(re.findall(r"add_job\(.*?id=['\"]([a-z0-9_]+)['\"]", text))


def test_main_ids_coinciden_con_registry():
    assert _main_job_ids() == set(CRON_JOB_IDS)


def test_expected_es_25():
    assert EXPECTED_CRON_JOBS == 25  # 24 + rex_publisher (DEBT-098)
    assert len(CRON_JOB_IDS) == 25
