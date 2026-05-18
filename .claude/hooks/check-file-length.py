#!/usr/bin/env python3
"""
OmegaRaisen — check-file-length.py
PostToolUse hook: warning >75L · error >100L.

Excepciones documentadas (DDD C4):
  · src/components/ui/* (shadcn autogenerado)
  · src/integrations/supabase/types.ts (autogenerado)
  · supabase/migrations/*.sql (SQL, no aplica regla de TS/Python)
"""

import json
import sys
from pathlib import Path

WARN_THRESHOLD = 75
ERROR_THRESHOLD = 100

EXEMPTIONS = [
    "src/components/ui/",
    "src/integrations/supabase/types.ts",
    "supabase/migrations/",
    "backend/app/bc_cognition/domain/limits_omega.py",   # G1: contrato inmutable
    "/__pycache__/",
    "/node_modules/",
    "/.git/",
    ".test.",
    "test_",
    "/tests/",
]


def is_exempt(path: str) -> bool:
    return any(exempt in path for exempt in EXEMPTIONS)


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "str_replace", "create_file"):
        return 0

    target = (
        payload.get("tool_input", {}).get("path")
        or payload.get("tool_input", {}).get("file_path")
    )

    if not target:
        return 0

    target = str(Path(target)).replace("\\", "/")

    if is_exempt(target):
        return 0

    # Solo aplica a archivos de código fuente
    if not target.endswith((".py", ".ts", ".tsx", ".js", ".jsx")):
        return 0

    try:
        with open(target, "r", encoding="utf-8") as f:
            line_count = sum(1 for _ in f)
    except (FileNotFoundError, OSError):
        return 0

    if line_count > ERROR_THRESHOLD:
        print(
            f"""
╔═══════════════════════════════════════════════════════════════╗
║  ⛔ ARCHIVO >100 LÍNEAS — VIOLA DDD C4                         ║
╚═══════════════════════════════════════════════════════════════╝

Archivo:  {target}
Líneas:   {line_count}
Límite:   ≤ {ERROR_THRESHOLD} (error) · ≤ {WARN_THRESHOLD} (warning)

Refactor obligatorio. Opciones:
  · Extraer función/clase a archivo separado
  · Dividir en bounded context si es muy grande
  · Si es legacy: agregar a deuda técnica en SOURCE_OF_TRUTH.md
                  con commit message "fix(debt): track {target}"
""",
            file=sys.stderr,
        )
        return 1

    if line_count > WARN_THRESHOLD:
        print(
            f"⚠ {target}: {line_count} líneas (límite recomendado: {WARN_THRESHOLD}). Considera refactor.",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
