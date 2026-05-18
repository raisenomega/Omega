#!/bin/bash
# OMEGA SENTINEL — Morning Check
# Uso: bash sentinel_check.sh
# Claude Code lee SENTINEL, diagnostica, y propone fixes

claude "
Ciclo de auditoría SENTINEL:

PASO 1 — Lee el estado actual:
  GET https://omegaraisen-production-2031.up.railway.app/api/v1/sentinel/status/
  GET https://omegaraisen-production-2031.up.railway.app/api/v1/sentinel/history/?limit=1

PASO 2 — Si score = 100:
  Responde: SENTINEL OK — sistema limpio. Score 100/100.
  Fin.

PASO 3 — Si score < 100:
  Lee cada issue del último scan.
  Para cada issue:
    a) Identifica el archivo local afectado con grep
    b) Lee el archivo
    c) Propón el fix exacto con diff
    d) ESPERA MI CONFIRMACIÓN antes de aplicar

PASO 4 — Después de que yo apruebe cada fix:
  Aplica el cambio
  git add + git commit con mensaje descriptivo
  git push
  POST https://omegaraisen-production-2031.up.railway.app/api/v1/sentinel/register-fix
    con: error_type, file_path, symptom, root_cause, fix_description,
         rule_code (genera uno nuevo tipo R-SENT-XXX), rule_text, prevention

PASO 5 — Re-ejecuta el scan para confirmar que el fix funcionó:
  POST /api/v1/sentinel/scan/ con scan_type=full
  Si score = 100 → CICLO COMPLETO ✅
  Si score < 100 → repite desde PASO 3 para los issues restantes
"
