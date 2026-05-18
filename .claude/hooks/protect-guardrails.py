#!/usr/bin/env python3
"""
OmegaRaisen — protect-guardrails.py
PreToolUse hook: bloquea modificaciones a archivos protegidos sin firma del owner.

Archivos protegidos:
  · backend/app/bc_cognition/domain/limits_omega.py
  · scripts/guardrails-sha1.txt
  · .claude/hooks/*
  · .claude/settings.json
  · DDD_REGLAS_OMEGA.md

Para modificar uno de estos: el commit message debe incluir "OWNER_APPROVED: <razón>".
"""

import json
import os
import sys
from pathlib import Path

PROTECTED_PATHS = [
    "backend/app/bc_cognition/domain/limits_omega.py",
    "scripts/guardrails-sha1.txt",
    "DDD_REGLAS_OMEGA.md",
    "CLAUDE.md",
]

PROTECTED_DIRS = [
    ".claude/hooks/",
    ".claude/agents/",
]


def main() -> int:
    """Lee el payload del hook desde stdin (Claude Code format)."""
    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        # No payload válido — permitir (no es un hook de Claude Code)
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "str_replace", "create_file"):
        return 0

    # Detectar el path target del tool
    target_path = (
        payload.get("tool_input", {}).get("path")
        or payload.get("tool_input", {}).get("file_path")
        or ""
    )

    if not target_path:
        return 0

    # Normalizar
    target_path = str(Path(target_path)).replace("\\", "/")

    # Check 1: archivos protegidos exactos
    for protected in PROTECTED_PATHS:
        if target_path.endswith(protected):
            print_warning(target_path, protected)
            return 1

    # Check 2: directorios protegidos
    for protected_dir in PROTECTED_DIRS:
        if protected_dir in target_path:
            print_warning(target_path, protected_dir)
            return 1

    return 0


def print_warning(target: str, protected: str) -> None:
    print(
        f"""
╔═══════════════════════════════════════════════════════════════╗
║  ⛔ MODIFICACIÓN BLOQUEADA POR PROTECT-GUARDRAILS HOOK         ║
╚═══════════════════════════════════════════════════════════════╝

Archivo:    {target}
Categoría:  {protected}

Este archivo está protegido por hook PreToolUse.

Para modificarlo legítimamente:

  1. Verifica que tienes aprobación firmada del owner
  2. Documenta la razón en el commit message:
       OWNER_APPROVED: <razón concisa del cambio>
  3. Si es limits_omega.py:
       a) Commit primero un test que falla con los valores nuevos
       b) Tras el cambio: bash scripts/verify-guardrails.sh --update
       c) Commit del nuevo SHA1 baseline en el MISMO PR
  4. Si es un hook o agente:
       Aprobación explícita del owner en el PR description

🐢💎 Estos archivos son contrato — no se editan al vuelo.
""",
        file=sys.stderr,
    )


if __name__ == "__main__":
    sys.exit(main())
