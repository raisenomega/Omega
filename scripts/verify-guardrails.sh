#!/usr/bin/env bash
# OmegaRaisen — verify-guardrails.sh
# Verifica que el SHA1 de limits_omega.py coincida con el baseline registrado.
# Si NO coincide: alguien modificó los guardrails — bloquea.
#
# Uso:
#   bash scripts/verify-guardrails.sh                    # verifica
#   bash scripts/verify-guardrails.sh --update           # actualiza baseline (con cuidado!)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

GUARDRAILS_FILE="backend/app/bc_cognition/domain/limits_omega.py"
BASELINE_FILE="scripts/guardrails-sha1.txt"

if [ ! -f "$GUARDRAILS_FILE" ]; then
  echo -e "${RED}✗ $GUARDRAILS_FILE no existe${NC}"
  echo "  Este archivo es G1 — debe existir en bc_cognition/domain/"
  exit 2
fi

ACTUAL_SHA=$(sha1sum "$GUARDRAILS_FILE" | awk '{print $1}')

# Modo update
if [ "${1:-}" = "--update" ]; then
  echo -e "${YELLOW}⚠ MODO UPDATE — actualizando baseline${NC}"
  echo ""
  echo "  Archivo:        $GUARDRAILS_FILE"
  echo "  SHA1 nuevo:     $ACTUAL_SHA"
  echo ""
  echo "  ¿Confirmas la actualización? Esto significa que:"
  echo "    1. Has commiteado un test que verifica el nuevo valor"
  echo "    2. El owner aprobó el cambio en el PR description"
  echo "    3. Documentaste el rollback plan"
  echo ""
  read -rp "  Confirma escribiendo 'CAMBIO APROBADO': " confirmation

  if [ "$confirmation" = "CAMBIO APROBADO" ]; then
    echo "$ACTUAL_SHA  $GUARDRAILS_FILE" > "$BASELINE_FILE"
    echo -e "${GREEN}✓ Baseline actualizado: $ACTUAL_SHA${NC}"
    echo ""
    echo "  Próximos pasos:"
    echo "    git add $BASELINE_FILE $GUARDRAILS_FILE"
    echo "    git commit -m \"chore(guardrails): rotate SHA1 baseline · approved by owner\""
    exit 0
  else
    echo -e "${RED}✗ Confirmación no recibida — baseline NO actualizado${NC}"
    exit 1
  fi
fi

# Modo verificación normal
if [ ! -f "$BASELINE_FILE" ]; then
  echo -e "${YELLOW}⚠ $BASELINE_FILE no existe — creando baseline inicial${NC}"
  echo "$ACTUAL_SHA  $GUARDRAILS_FILE" > "$BASELINE_FILE"
  echo -e "${GREEN}✓ Baseline creado: $ACTUAL_SHA${NC}"
  exit 0
fi

EXPECTED_SHA=$(awk '{print $1}' "$BASELINE_FILE")

if [ "$ACTUAL_SHA" = "$EXPECTED_SHA" ]; then
  echo -e "${GREEN}✓ Guardrails intactos${NC}"
  echo "  $GUARDRAILS_FILE"
  echo "  SHA1: $ACTUAL_SHA"
  exit 0
else
  echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${RED}║  ✗ GUARDRAILS MODIFICADOS                                     ║${NC}"
  echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
  echo ""
  echo "  Archivo:    $GUARDRAILS_FILE"
  echo "  Esperado:   $EXPECTED_SHA"
  echo "  Actual:     $ACTUAL_SHA"
  echo ""
  echo "  Si el cambio es INTENCIONAL:"
  echo "    1. Verifica que existe un test que falla con los valores viejos"
  echo "    2. Verifica que el owner aprobó el cambio"
  echo "    3. Ejecuta: bash scripts/verify-guardrails.sh --update"
  echo ""
  echo "  Si el cambio NO es intencional:"
  echo "    git diff $GUARDRAILS_FILE     # ver qué cambió"
  echo "    git checkout $GUARDRAILS_FILE # revertir"
  echo ""
  echo "🐢💎 Modificar guardrails sin proceso = compromiso de seguridad."
  exit 1
fi
