#!/usr/bin/env bash
# OmegaRaisen — verify-on-stop.sh
# Stop hook: verifica el estado antes de terminar la sesión.
# No bloquea — solo reporta. El owner decide si commitea o no.

set +e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 0

echo ""
echo -e "${CYAN}═══ Stop hook · verify-on-stop ═══${NC}"

# 1. SHA1 de guardrails intacto
if [ -f scripts/verify-guardrails.sh ]; then
  if ! bash scripts/verify-guardrails.sh > /dev/null 2>&1; then
    echo -e "${RED}  ✗ Guardrails SHA1 modificado — revisar antes de push${NC}"
  else
    echo -e "${GREEN}  ✓ Guardrails SHA1 OK${NC}"
  fi
fi

# 2. Archivos modificados en la sesión (resumen)
if [ -d .git ]; then
  MODIFIED=$(git diff --name-only 2>/dev/null | wc -l)
  STAGED=$(git diff --cached --name-only 2>/dev/null | wc -l)
  UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l)

  echo -e "${CYAN}  Archivos modificados:${NC}   $MODIFIED"
  echo -e "${CYAN}  Archivos staged:${NC}        $STAGED"
  echo -e "${CYAN}  Archivos sin trackear:${NC}  $UNTRACKED"

  if [ "$MODIFIED" -gt 0 ] || [ "$STAGED" -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}  📋 Próximo paso recomendado:${NC}"
    echo "      bash scripts/validate-before-push.sh"
    echo "      git add . && git commit -m \"<scope>: <description>\""
  fi
fi

# 3. Tests rápidos (no bloquea)
echo -e "${CYAN}  Tests:${NC}"
if [ -d backend ] && command -v pytest &>/dev/null; then
  PYTEST_OUT=$(cd backend && timeout 60 pytest -q 2>&1 | tail -2 || true)
  if echo "$PYTEST_OUT" | grep -qE 'failed'; then
    echo -e "    ${RED}✗ Pytest: $PYTEST_OUT${NC}"
  elif echo "$PYTEST_OUT" | grep -qE 'passed'; then
    echo -e "    ${GREEN}✓ Pytest: $PYTEST_OUT${NC}"
  fi
fi

echo ""
echo "🐢💎 No velocity, only precision."
echo ""

exit 0
