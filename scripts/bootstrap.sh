#!/usr/bin/env bash
# OmegaRaisen — bootstrap.sh
# Setup inicial one-shot del entorno de desarrollo.
#
# Idempotente: se puede correr múltiples veces sin daño.
# Uso: bash scripts/bootstrap.sh

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  OmegaRaisen — Bootstrap inicial                              ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ─── Paso 1: verificar prerequisitos ──────────────────────────────
echo -e "${CYAN}[1/8] Verificando prerequisitos...${NC}"

check_command() {
  if ! command -v "$1" &>/dev/null; then
    echo -e "${RED}  ✗ $1 no encontrado${NC}"
    echo "    Instalar: $2"
    return 1
  else
    echo -e "${GREEN}  ✓ $1 — $(command -v "$1")${NC}"
  fi
}

MISSING=0
check_command node     "https://nodejs.org/ (≥20 LTS)"           || MISSING=$((MISSING+1))
check_command npm      "viene con Node.js"                        || MISSING=$((MISSING+1))
# Python 3.11 detection — supports py launcher (Windows), python3.11, or python3 if it is 3.11
PYTHON311=""
if command -v py &>/dev/null && py -3.11 --version &>/dev/null; then
  PYTHON311="py -3.11"
  echo -e "${GREEN}  ✓ python 3.11 — $(py -3.11 --version) (via py launcher)${NC}"
elif command -v python3.11 &>/dev/null; then
  PYTHON311="python3.11"
  echo -e "${GREEN}  ✓ python3.11 — $(command -v python3.11)${NC}"
elif command -v python3 &>/dev/null && python3 --version 2>&1 | grep -q "Python 3\.11"; then
  PYTHON311="python3"
  echo -e "${GREEN}  ✓ python3 — $(command -v python3) ($(python3 --version 2>&1))${NC}"
else
  echo -e "${RED}  ✗ Python 3.11 no encontrado${NC}"
  echo "    Instalar: winget install Python.Python.3.11 (Windows) o https://www.python.org/"
  MISSING=$((MISSING+1))
fi
check_command git      "https://git-scm.com/"                     || MISSING=$((MISSING+1))
check_command supabase "npm install -g supabase"                  || true  # opcional

[ "$MISSING" -gt 0 ] && {
  echo ""
  echo -e "${RED}✗ Faltan $MISSING herramientas. Instalar y volver a correr.${NC}"
  exit 1
}

# ─── Paso 2: identidad git ────────────────────────────────────────
echo ""
echo -e "${CYAN}[2/8] Verificando identidad git...${NC}"

USER_EMAIL=$(git config user.email 2>/dev/null || echo "")
USER_NAME=$(git config user.name 2>/dev/null || echo "")

EXPECTED_EMAIL="raisenagencypr@gmail.com"

if [ "$USER_EMAIL" = "$EXPECTED_EMAIL" ]; then
  echo -e "${GREEN}  ✓ user.email = $USER_EMAIL${NC}"
  echo -e "${GREEN}  ✓ user.name  = $USER_NAME${NC}"
else
  echo -e "${YELLOW}  ⚠ user.email actual: $USER_EMAIL${NC}"
  echo -e "${YELLOW}  ⚠ Esperado:          $EXPECTED_EMAIL${NC}"
  echo ""
  echo "  Configurar includeIf según PROTOCOLO_IDENTIDAD_GIT_OMEGA.md:"
  echo ""
  echo "    [includeIf \"gitdir:$ROOT_DIR/\"]"
  echo "      path = ~/.gitconfig-raisen"
  echo ""
  echo "  Crea ~/.gitconfig-raisen con:"
  echo ""
  echo "    [user]"
  echo "      name = raisenomega"
  echo "      email = $EXPECTED_EMAIL"
  echo ""
  echo "  ¿Continuar de todas formas? (no recomendado)"
  read -rp "  Escribe 'sí' para continuar: " confirm
  [ "$confirm" != "sí" ] && exit 1
fi

# ─── Paso 3: .env ─────────────────────────────────────────────────
echo ""
echo -e "${CYAN}[3/8] Verificando .env...${NC}"

if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo -e "${YELLOW}  ⚠ .env creado desde .env.example${NC}"
    echo -e "${YELLOW}  ⚠ EDITA .env con tus credenciales antes de continuar${NC}"
  else
    echo -e "${RED}  ✗ .env.example no encontrado${NC}"
    exit 1
  fi
else
  echo -e "${GREEN}  ✓ .env existe${NC}"
fi

# ─── Paso 4: Frontend deps ────────────────────────────────────────
echo ""
echo -e "${CYAN}[4/8] Instalando dependencias frontend...${NC}"

if [ -f package.json ]; then
  npm install --no-audit --no-fund
  echo -e "${GREEN}  ✓ npm install completado${NC}"
else
  echo -e "${YELLOW}  ⚠ package.json no encontrado (Fase 1 incompleta?)${NC}"
fi

# ─── Paso 5: Backend deps ─────────────────────────────────────────
echo ""
echo -e "${CYAN}[5/8] Instalando dependencias backend...${NC}"

if [ -f backend/requirements.txt ]; then
  cd backend

  if [ ! -d venv ]; then
    $PYTHON311 -m venv venv
    echo -e "${GREEN}  ✓ venv creado (Python 3.11)${NC}"
  fi

  # shellcheck disable=SC1091
  source venv/bin/activate 2>/dev/null || source venv/Scripts/activate
  python -m pip install --quiet --upgrade pip
  python -m pip install --quiet -r requirements.txt
  echo -e "${GREEN}  ✓ pip install completado${NC}"

  cd ..
else
  echo -e "${YELLOW}  ⚠ backend/requirements.txt no encontrado${NC}"
fi

# ─── Paso 6: Permisos de scripts ──────────────────────────────────
echo ""
echo -e "${CYAN}[6/8] Configurando permisos de scripts...${NC}"

for script in scripts/*.sh; do
  if [ -f "$script" ]; then
    chmod +x "$script"
    echo -e "${GREEN}  ✓ $script ejecutable${NC}"
  fi
done

# ─── Paso 7: Git hooks ────────────────────────────────────────────
echo ""
echo -e "${CYAN}[7/8] Instalando git hooks...${NC}"

if [ -d .git ]; then
  if [ -f scripts/validate-before-push.sh ]; then
    cp scripts/validate-before-push.sh .git/hooks/pre-push
    chmod +x .git/hooks/pre-push
    echo -e "${GREEN}  ✓ pre-push hook instalado${NC}"
  fi
else
  echo -e "${YELLOW}  ⚠ No es un repo git (¿correr git init?)${NC}"
fi

# ─── Paso 8: Verificación inicial ─────────────────────────────────
echo ""
echo -e "${CYAN}[8/8] Verificación inicial...${NC}"

if [ -f scripts/verify-guardrails.sh ]; then
  bash scripts/verify-guardrails.sh
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✓ Bootstrap completo                                         ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Próximos pasos:"
echo ""
echo "  1. Edita .env con tus credenciales reales"
echo "  2. Aplica migraciones de Supabase:"
echo "       supabase link --project-ref rwlnihoqhxwpbehibgxu"
echo "       supabase db push"
echo "  3. Levanta el stack en dos terminales:"
echo "       Terminal 1:  npm run dev"
echo "       Terminal 2:  cd backend && uvicorn app.main:app --reload"
echo "  4. Antes del primer commit:"
echo "       bash scripts/validate-before-push.sh"
echo ""
echo "🐢💎 No velocity, only precision."
