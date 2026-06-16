#!/usr/bin/env bash
# X1 PRE-DEPLOY (no es check del gate pre-push) · aborta si el security_score de
# SENTINEL < 95. Lee GET /api/v1/sentinel/status/ (campo .security_score) con un
# token superadmin. Requiere jq.
#   Uso: RAILWAY_URL=https://... SENTINEL_DEPLOY_TOKEN=<jwt superadmin> bash scripts/check-sentinel-score.sh
set -uo pipefail

MIN=95
URL="${RAILWAY_URL:-https://omega-production-3c67.up.railway.app}"
TOKEN="${SENTINEL_DEPLOY_TOKEN:-}"

if [ -z "$TOKEN" ]; then
  echo "⚠ X1: SENTINEL_DEPLOY_TOKEN no seteado — check omitido (no bloquea · setealo para activar)"
  exit 0
fi

SCORE=$(curl -s -m 30 -H "Authorization: Bearer $TOKEN" "$URL/api/v1/sentinel/status/" | jq -r '.security_score // empty')
if [ -z "$SCORE" ]; then
  echo "❌ X1: no se pudo leer .security_score de $URL/api/v1/sentinel/status/ (¿token? ¿endpoint?)"
  exit 1
fi
if [ "$(printf '%.0f' "$SCORE")" -lt "$MIN" ]; then
  echo "❌ X1: SENTINEL score $SCORE < $MIN — deploy BLOQUEADO"
  exit 1
fi
echo "✓ X1: SENTINEL score $SCORE ≥ $MIN — deploy OK"
