#!/usr/bin/env bash
# OmegaRaisen — verify-personas.sh
# Verifica que el SHA1 de las personas (system prompts) coincida con el baseline.
# Regla X2: las personas (NOVA/ARIA) son INMUTABLES. Si NO coinciden: alguien
# modificó un system prompt — bloquea.
#
# Uso:
#   bash scripts/verify-personas.sh              # verifica
#   bash scripts/verify-personas.sh --update     # rota baseline (con cuidado!)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PERSONA_FILES=(
  "backend/app/bc_cognition/domain/persona_nova.py"
  "backend/app/bc_cognition/domain/persona_aria.py"
)
BASELINE_FILE="scripts/personas-sha1.txt"

for f in "${PERSONA_FILES[@]}"; do
  if [ ! -f "$f" ]; then
    echo -e "${RED}✗ $f no existe${NC}"
    echo "  Es una persona X2 — debe existir en bc_cognition/domain/"
    exit 2
  fi
done

compute_sha() { sha1sum "$1" | awk '{print $1}'; }

# Modo update — rota el baseline tras aprobación owner (ritual X2)
if [ "${1:-}" = "--update" ]; then
  echo -e "${YELLOW}⚠ MODO UPDATE — rotando baseline de personas${NC}"
  echo ""
  for f in "${PERSONA_FILES[@]}"; do
    echo "  $f → $(compute_sha "$f")"
  done
  echo ""
  echo "  ¿Confirmas la rotación? Esto significa que:"
  echo "    1. El cambio de system prompt fue revisado (test/diff)"
  echo "    2. El owner aprobó el cambio (regla X2)"
  echo "    3. Documentaste el rollback plan"
  echo ""
  read -rp "  Confirma escribiendo 'CAMBIO APROBADO': " confirmation

  if [ "$confirmation" = "CAMBIO APROBADO" ]; then
    : > "$BASELINE_FILE"
    for f in "${PERSONA_FILES[@]}"; do
      echo "$(compute_sha "$f")  $f" >> "$BASELINE_FILE"
    done
    echo -e "${GREEN}✓ Baseline de personas rotado${NC}"
    echo ""
    echo "  Próximos pasos:"
    echo "    git add $BASELINE_FILE ${PERSONA_FILES[*]}"
    echo "    git commit -m \"chore(personas): rotate SHA1 baseline · approved by owner\""
    exit 0
  else
    echo -e "${RED}✗ Confirmación no recibida — baseline NO rotado${NC}"
    exit 1
  fi
fi

# Modo verificación normal
if [ ! -f "$BASELINE_FILE" ]; then
  echo -e "${YELLOW}⚠ $BASELINE_FILE no existe — creando baseline inicial${NC}"
  : > "$BASELINE_FILE"
  for f in "${PERSONA_FILES[@]}"; do
    echo "$(compute_sha "$f")  $f" >> "$BASELINE_FILE"
  done
  echo -e "${GREEN}✓ Baseline creado${NC}"
  exit 0
fi

FAIL=0
while read -r expected path; do
  [ -z "$expected" ] && continue
  actual=$(compute_sha "$path")
  if [ "$expected" != "$actual" ]; then
    echo -e "${RED}✗ Persona modificada: $(basename "$path")${NC}"
    echo "  Esperado:   $expected"
    echo "  Actual:     $actual"
    FAIL=1
  fi
done < "$BASELINE_FILE"

if [ "$FAIL" -eq 0 ]; then
  echo -e "${GREEN}✓ Personas intactas (NOVA + ARIA)${NC}"
  exit 0
fi

echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║  ✗ PERSONA(S) MODIFICADA(S) — viola X2 (inmutabilidad)        ║${NC}"
echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  Si el cambio es INTENCIONAL:"
echo "    1. Verifica que el cambio de prompt fue revisado (diff)"
echo "    2. Verifica que el owner aprobó (regla X2)"
echo "    3. Ejecuta: bash scripts/verify-personas.sh --update"
echo ""
echo "  Si NO es intencional:"
echo "    git diff backend/app/bc_cognition/domain/persona_*.py"
echo "    git checkout backend/app/bc_cognition/domain/persona_*.py"
echo ""
echo "🐢💎 Modificar una persona sin proceso = compromiso de gobierno IA."
exit 1
