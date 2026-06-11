"""P0-1 regresion · auditoria externa 10 jun 2026.

Guard: mientras main.py registre APScheduler in-process (scheduler.start()),
nixpacks.toml DEBE arrancar uvicorn con --workers 1. >1 worker sin locking
distribuido = cada worker dispara los 24 crons = doble publicacion (viola P2).
Acompana al check 12 de validate-before-push.sh (defensa en profundidad: el
script bloquea el push a mano, este test bloquea via pytest del gate)."""
import re
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[2]
_NIXPACKS = _BACKEND / "nixpacks.toml"
_MAIN = _BACKEND / "app" / "main.py"


def _uvicorn_workers() -> int:
    """Lee el N de `--workers N` del cmd [start] de nixpacks.toml."""
    text = _NIXPACKS.read_text(encoding="utf-8")
    m = re.search(r"--workers[=\s]+(\d+)", text)
    assert m, "no se encontro --workers en nixpacks.toml [start]"
    return int(m.group(1))


def test_single_worker_while_scheduler_in_process():
    """Si main.py corre el scheduler in-process → nixpacks debe usar 1 worker."""
    main_src = _MAIN.read_text(encoding="utf-8")
    scheduler_in_process = "scheduler.start()" in main_src
    if scheduler_in_process:
        assert _uvicorn_workers() == 1, (
            "P0-1: main.py corre APScheduler in-process (scheduler.start()) pero "
            "nixpacks arranca >1 worker -> crons duplicados. Usa --workers 1 o "
            "extrae el scheduler a proceso propio (DEBT-SCHEDULER-SPLIT)."
        )


def test_nixpacks_workers_parseable():
    """El guard solo sirve si el formato es legible · falla ruidoso si cambia."""
    assert _uvicorn_workers() >= 1
