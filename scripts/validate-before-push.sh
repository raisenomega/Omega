#!/usr/bin/env bash
# OmegaRaisen — validate-before-push.sh
# Ejecuta los 9 checks zero-tolerance del DDD_REGLAS_OMEGA.md
# Bloquea el push si CUALQUIERA falla.
#
# Uso:
#   bash scripts/validate-before-push.sh
#
# Para activarlo como pre-push hook:
#   cp scripts/validate-before-push.sh .git/hooks/pre-push
#   chmod +x .git/hooks/pre-push

set -uo pipefail

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

FAILURES=0
WARNINGS=0
TOTAL=12

print_header() { echo -e "\n${CYAN}═══ $1 ═══${NC}"; }
print_pass()   { echo -e "${GREEN}✓ $1${NC}"; }
print_fail()   { echo -e "${RED}✗ $1${NC}"; FAILURES=$((FAILURES+1)); }
print_warn()   { echo -e "${YELLOW}⚠ $1${NC}"; WARNINGS=$((WARNINGS+1)); }

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  OmegaRaisen — validate-before-push (DDD enforcement)         ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"

# ─────────────────────────────────────────────────────────────────
# CHECK 0/10 — IDENTIDAD GIT (BLOQUEANTE · ver IDENTIDAD_GIT_CRITICA.md)
# ─────────────────────────────────────────────────────────────────
print_header "0/$TOTAL · Identidad git (bloqueante)"

EXPECTED_EMAIL="raisenagencypr@gmail.com"
EXPECTED_NAME="raisenomega"
ACTUAL_EMAIL=$(git config --get user.email 2>/dev/null || echo "")
ACTUAL_NAME=$(git config --get user.name 2>/dev/null || echo "")

if [ "$ACTUAL_EMAIL" = "$EXPECTED_EMAIL" ] && [ "$ACTUAL_NAME" = "$EXPECTED_NAME" ]; then
  print_pass "Identidad: $ACTUAL_NAME <$ACTUAL_EMAIL>"
else
  print_fail "Identidad git incorrecta"
  echo "    user.name actual:   '$ACTUAL_NAME'     (esperado: '$EXPECTED_NAME')"
  echo "    user.email actual:  '$ACTUAL_EMAIL'    (esperado: '$EXPECTED_EMAIL')"
  echo ""
  echo "    Lee IDENTIDAD_GIT_CRITICA.md §3 para configurar el includeIf."
  echo "    Push BLOQUEADO hasta corregir identidad."
fi

# ─────────────────────────────────────────────────────────────────
# CHECK 1/10 — C1+C2: Cero `any` en TS / Cero `Any` en Python
# ─────────────────────────────────────────────────────────────────
print_header "1/$TOTAL · C1+C2 — Cero \`any\` / @ts-ignore / type: ignore"

TS_VIOLATIONS=$(grep -rnE ':\s*any\b|as any\b|@ts-ignore' src/ --include="*.ts" --include="*.tsx" 2>/dev/null \
  | grep -v 'src/components/ui/' \
  | grep -v 'src/integrations/supabase/types.ts' \
  | grep -v '\.test\.' \
  | grep -v '// eslint-disable' \
  | grep -v 'src/pages/' \
  | grep -v 'src/hooks/' \
  | grep -v 'src/components/clients/' \
  || true)
# Las 3 últimas exclusiones son grace period DEBT-015 (Fase 2 §2.2 lift & shift).
# Re-aplicar el check estricto al cerrar DEBT-015 durante Fase 3 §3.2 refactor por BC.

if [ -n "$TS_VIOLATIONS" ]; then
  print_fail "TypeScript \`any\` / @ts-ignore detectado:"
  echo "$TS_VIOLATIONS" | head -10
  [ $(echo "$TS_VIOLATIONS" | wc -l) -gt 10 ] && echo "  ... y más"
else
  print_pass "Sin \`any\` ni @ts-ignore en frontend"
fi

PY_VIOLATIONS=$(grep -rnE ':\s*Any\b|cast\(Any|# type: ignore' backend/app/ --include="*.py" 2>/dev/null \
  | grep -v '\.test\.' \
  | grep -v 'test_' \
  | grep -v '/tests/' \
  | grep -v 'bc_cognition/domain/limits_omega.py' \
  | grep -v 'backend/app/agents/' \
  | grep -v 'backend/app/infrastructure/ai/providers/' \
  | grep -v 'backend/app/models/' \
  || true)
# Las 3 últimas exclusiones (agents/, infrastructure/ai/providers/, models/) son grace
# period DEBT-016 (Fase 2 §2.1 lift & shift backend). Re-aplicar el check estricto al
# cerrar DEBT-016 durante Fase 2 §2.4-§2.6 hot-swap de providers.

if [ -n "$PY_VIOLATIONS" ]; then
  print_fail "Python \`Any\` / type: ignore detectado:"
  echo "$PY_VIOLATIONS" | head -10
else
  print_pass "Sin \`Any\` ni type: ignore en backend"
fi

# ─────────────────────────────────────────────────────────────────
# CHECK 2/10 — I1: Solo Anthropic (con excepciones Nano Banana + Veo 3.1)
# ─────────────────────────────────────────────────────────────────
print_header "2/$TOTAL · I1 — Solo Anthropic (excepciones documentadas)"

# Imports prohibidos absolutos
PROHIBITED=$(grep -rnE 'from\s+(openai|groq|deepseek|mistralai|runwayml|fal_client)\b|import\s+(openai|groq|deepseek|mistralai|runwayml|fal_client)\b' \
  backend/app/ src/ --include="*.py" --include="*.ts*" 2>/dev/null \
  | grep -v '\.test\.' \
  | grep -v 'test_' \
  | grep -v '/tests/' \
  || true)
# Fase 2 §2.6 (18 may 2026): cerrado DEBT-016 · 100% I1 compliance achieved.
# Todos los providers prohibidos (openai/groq/deepseek/gemini-texto/runway/fal_client)
# fueron eliminados o reemplazados por claude_service / anthropic_adapter / Nano Banana / Veo 3.1.

if [ -n "$PROHIBITED" ]; then
  print_fail "I1 violado — proveedor IA prohibido:"
  echo "$PROHIBITED" | head -10
else
  print_pass "Sin imports de openai/groq/deepseek/mistralai/runwayml/fal_client"
fi

# Google GenAI solo permitido en los 2 adapters autorizados
ILLEGAL_GENAI=$(grep -rnE 'from\s+google\.genai|from\s+google_genai|import\s+google\.genai' \
  backend/app/ --include="*.py" 2>/dev/null \
  | grep -vE 'bc_cognition/infrastructure/(nano_banana|veo3)_adapter\.py' || true)

if [ -n "$ILLEGAL_GENAI" ]; then
  print_fail "I1 violado — google-genai fuera de adapters autorizados:"
  echo "$ILLEGAL_GENAI" | head -10
else
  print_pass "google-genai solo en bc_cognition/infrastructure/{nano_banana,veo3}_adapter.py"
fi

# Voyage AI (embeddings) solo permitido en el adapter autorizado (DEBT-048 · EXCEPCIÓN 3)
ILLEGAL_VOYAGE=$(grep -rnE 'from\s+voyageai|import\s+voyageai' \
  backend/app/ --include="*.py" 2>/dev/null \
  | grep -vE 'bc_cognition/infrastructure/voyage_adapter\.py' || true)

if [ -n "$ILLEGAL_VOYAGE" ]; then
  print_fail "I1 violado — voyageai fuera del adapter autorizado:"
  echo "$ILLEGAL_VOYAGE" | head -10
else
  print_pass "voyageai solo en bc_cognition/infrastructure/voyage_adapter.py"
fi

# ─────────────────────────────────────────────────────────────────
# CHECK 3/10 — A2: Domain puro (cero imports externos)
# ─────────────────────────────────────────────────────────────────
print_header "3/$TOTAL · A2 — Domain puro"

DOMAIN_VIOLATIONS=$(grep -rnE 'from\s+(anthropic|google|openai|supabase|fastapi|sqlalchemy|httpx|requests)' \
  backend/app/bc_cognition/domain/ \
  backend/app/domain/ \
  src/bc-*/domain/ \
  --include="*.py" --include="*.ts*" 2>/dev/null || true)

if [ -n "$DOMAIN_VIOLATIONS" ]; then
  print_fail "A2 violado — domain importa código externo:"
  echo "$DOMAIN_VIOLATIONS" | head -10
else
  print_pass "Domain layer pura (sin imports de infra)"
fi

# ─────────────────────────────────────────────────────────────────
# CHECK 4/10 — G6: Sin secretos hardcoded
# ─────────────────────────────────────────────────────────────────
print_header "4/$TOTAL · G6 — Cero secretos hardcoded"

# Patrones de secretos comunes
SECRET_PATTERNS=(
  'sk-ant-[a-zA-Z0-9_-]{20,}'                # Anthropic
  'sk_live_[a-zA-Z0-9]{20,}'                 # Stripe live
  'whsec_[a-zA-Z0-9]{20,}'                   # Stripe webhook
  'AIza[a-zA-Z0-9_-]{30,}'                   # Google API
  'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.'      # JWT
  'postgres://[^"]+:[^"]+@'                   # DB URLs con password
  'BRAVE_API_KEY\s*=\s*["'\''][a-zA-Z0-9]'   # Brave
)

SECRETS_FOUND=0
for pattern in "${SECRET_PATTERNS[@]}"; do
  MATCHES=$(grep -rnE "$pattern" backend/app/ src/ --include="*.py" --include="*.ts*" --include="*.js*" 2>/dev/null \
    | grep -v '\.test\.' \
    | grep -v 'test_' \
    | grep -v '/tests/' \
    | grep -v '\.example' || true)
  if [ -n "$MATCHES" ]; then
    print_fail "Secreto hardcoded detectado (patrón: $pattern):"
    echo "$MATCHES" | head -3
    SECRETS_FOUND=$((SECRETS_FOUND+1))
  fi
done

if [ "$SECRETS_FOUND" -eq 0 ]; then
  print_pass "Cero secretos hardcoded"
fi

# ─────────────────────────────────────────────────────────────────
# CHECK 5/10 — G9: Cero mock/fake/dummy en producción
# ─────────────────────────────────────────────────────────────────
print_header "5/$TOTAL · G9 — Cero mock/fake/dummy en código de producción"

MOCK_VIOLATIONS=$(grep -rnE 'mock|fake|dummy|placeholder|TODO_REMOVE' \
  backend/app/ src/ \
  --include="*.py" --include="*.ts*" 2>/dev/null \
  | grep -v '\.test\.' \
  | grep -v 'test_' \
  | grep -v '/tests/' \
  | grep -v 'mockData' \
  | grep -v '// mock for development' \
  | grep -iE 'mock|fake|dummy' || true)

if [ -n "$MOCK_VIOLATIONS" ]; then
  print_warn "Mock/fake/dummy detectado en código de producción:"
  echo "$MOCK_VIOLATIONS" | head -5
  [ $(echo "$MOCK_VIOLATIONS" | wc -l) -gt 5 ] && echo "  ... y más"
else
  print_pass "Sin mock/fake/dummy en producción"
fi

# ─────────────────────────────────────────────────────────────────
# CHECK 6/10 — G2: SHA1 de guardrails intacto
# ─────────────────────────────────────────────────────────────────
print_header "6/$TOTAL · G2 — SHA1 de limits_omega.py intacto"

if [ -f scripts/guardrails-sha1.txt ] && [ -f backend/app/bc_cognition/domain/limits_omega.py ]; then
  EXPECTED=$(awk '{print $1}' scripts/guardrails-sha1.txt)
  ACTUAL=$(sha1sum backend/app/bc_cognition/domain/limits_omega.py | awk '{print $1}')

  if [ "$EXPECTED" = "$ACTUAL" ]; then
    print_pass "SHA1 limits_omega.py = $ACTUAL"
  else
    print_fail "SHA1 cambió sin actualizar baseline"
    echo "    Esperado: $EXPECTED"
    echo "    Actual:   $ACTUAL"
    echo "    Si el cambio es intencional, actualizar scripts/guardrails-sha1.txt con el nuevo SHA1"
  fi
else
  print_warn "scripts/guardrails-sha1.txt o limits_omega.py no encontrado (¿primer commit?)"
fi

# ─────────────────────────────────────────────────────────────────
# CHECK 7/10 — C4: Archivos ≤100 líneas (error) · ≤75 (warning)
# ─────────────────────────────────────────────────────────────────
print_header "7/$TOTAL · C4 — Archivos ≤100 líneas"

OVER_100=$(find backend/app/ src/ \
  \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" \) \
  ! -path "*/components/ui/*" \
  ! -path "*/integrations/supabase/types.ts" \
  ! -path "*/bc_cognition/domain/limits_omega.py" \
  ! -path "*/__pycache__/*" \
  ! -path "*/node_modules/*" \
  ! -path "*/pages/*" \
  ! -path "*/hooks/*" \
  ! -path "*/components/clients/*" \
  ! -path "*/components/dashboard/*" \
  ! -path "*/components/layout/*" \
  ! -path "*/components/analytics/*" \
  ! -path "src/App.tsx" \
  ! -path "backend/app/agents/*" \
  ! -path "backend/app/api/*" \
  ! -path "backend/app/services/*" \
  ! -path "backend/app/sentinel/*" \
  ! -path "backend/app/workers/*" \
  ! -path "backend/app/models/*" \
  ! -path "backend/app/domain/*" \
  ! -path "backend/app/infrastructure/*" \
  ! -path "backend/app/main.py" \
  -exec wc -l {} \; 2>/dev/null \
  | awk '$1 > 100' | sort -rn | head -20 || true)
# Las 7 primeras exclusiones (pages/, hooks/, components/{clients,dashboard,layout,analytics}/,
# App.tsx) son grace period DEBT-014 (Fase 2 §2.2 frontend lift & shift, 15 archivos).
# Las 8 siguientes (backend/app/{agents,api,services,sentinel,workers,models,domain,infrastructure}/)
# son grace period DEBT-017 (Fase 2 §2.1 backend lift & shift, 163 archivos).
# Re-aplicar el check estricto archivo por archivo durante Fase 3 §3.3 split progresivo
# (cerrar DEBT-014 y DEBT-017). Nota: backend/app/bc_cognition/ NO está exento.

OVER_75=$(find backend/app/ src/ \
  \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" \) \
  ! -path "*/components/ui/*" \
  ! -path "*/integrations/supabase/types.ts" \
  ! -path "*/bc_cognition/domain/limits_omega.py" \
  ! -path "*/__pycache__/*" \
  ! -path "*/node_modules/*" \
  -exec wc -l {} \; 2>/dev/null \
  | awk '$1 > 75 && $1 <= 100' | wc -l || true)

if [ -n "$OVER_100" ]; then
  print_fail "Archivos >100 líneas (push bloqueado):"
  echo "$OVER_100" | head -10
  TOTAL_OVER_100=$(echo "$OVER_100" | wc -l)
  [ "$TOTAL_OVER_100" -gt 10 ] && echo "  ... y $((TOTAL_OVER_100 - 10)) más"
  echo ""
  echo "  Excepciones permitidas: src/components/ui/*, src/integrations/supabase/types.ts"
  echo "  Refactor obligatorio antes de push."
else
  print_pass "Cero archivos >100 líneas"
fi

if [ "$OVER_75" -gt 0 ]; then
  print_warn "$OVER_75 archivos entre 75-100 líneas (refactor recomendado)"
fi

# ─────────────────────────────────────────────────────────────────
# CHECK 8/10 — T4: TypeScript compila sin errores
# ─────────────────────────────────────────────────────────────────
print_header "8/$TOTAL · T4 — TypeScript strict compila"

if [ -f tsconfig.json ] && command -v npx &>/dev/null; then
  if npx tsc --noEmit 2>&1 | tail -20 | grep -qE 'error TS'; then
    print_fail "TypeScript errors:"
    npx tsc --noEmit 2>&1 | grep 'error TS' | head -10
  else
    print_pass "TypeScript compila sin errores"
  fi
else
  print_warn "tsconfig.json no encontrado o npx no disponible"
fi

# ─────────────────────────────────────────────────────────────────
# CHECK 9/10 — T5: Tests pasando (Vitest + Pytest)
# ─────────────────────────────────────────────────────────────────
print_header "9/$TOTAL · T5 — Tests pasando"

if [ -f package.json ] && grep -q '"test"' package.json; then
  if npm test --silent 2>&1 | tail -5 | grep -qE 'failed|FAIL'; then
    print_fail "Tests frontend (Vitest) fallando"
  else
    print_pass "Tests frontend OK"
  fi
fi

# CHECK 9 backend · invoca pytest vía el venv directo (cross-platform · sin dep de PATH)
# PY_VENV es relativo a backend/ (POSIX: venv/bin/python · Windows: venv/Scripts/python.exe)
PY_VENV=""
if [ -x backend/venv/bin/python ]; then PY_VENV="venv/bin/python"
elif [ -x backend/venv/Scripts/python.exe ]; then PY_VENV="venv/Scripts/python.exe"
fi

if [ -d backend ] && [ -n "$PY_VENV" ]; then
  if (cd backend && "$PY_VENV" -m pytest -q 2>&1 | tail -3 | grep -qE 'failed|FAIL'); then
    print_fail "Tests backend (Pytest) fallando"
  else
    print_pass "Tests backend OK"
  fi
else
  print_warn "venv no encontrado en backend/venv/ — corré bootstrap.sh"
fi

# ─────────────────────────────────────────────────────────────────
# CHECK 10/11 — X2: SHA1 de personas (system prompts) intacto
# ─────────────────────────────────────────────────────────────────
print_header "10/$TOTAL · X2 — SHA1 de personas (NOVA/ARIA) intacto"

if [ -f scripts/personas-sha1.txt ]; then
  PERSONA_FAIL=0
  while read -r expected path; do
    [ -z "$expected" ] && continue
    if [ ! -f "$path" ]; then
      print_fail "Persona no encontrada: $path"; PERSONA_FAIL=1; continue
    fi
    actual=$(sha1sum "$path" | awk '{print $1}')
    if [ "$expected" != "$actual" ]; then
      print_fail "SHA1 cambió en $(basename "$path") sin rotar baseline"
      echo "    Esperado: $expected"
      echo "    Actual:   $actual"
      echo "    Si es intencional: bash scripts/verify-personas.sh --update (requiere aprobación owner · X2)"
      PERSONA_FAIL=1
    fi
  done < scripts/personas-sha1.txt
  [ "$PERSONA_FAIL" -eq 0 ] && print_pass "Personas intactas (NOVA + ARIA)"
else
  print_warn "scripts/personas-sha1.txt no encontrado (¿primer commit?)"
fi

# ─────────────────────────────────────────────────────────────────
# CHECK 12 (P0-1) — multi-worker + scheduler in-process = crons duplicados
# (display 11/$TOTAL · "check 12" = 12.º check 1-based · auditoría 10 jun 2026)
# ─────────────────────────────────────────────────────────────────
print_header "11/$TOTAL · P0-1 — Anti crons duplicados (workers vs scheduler)"

P01_NIXPACKS="backend/nixpacks.toml"
P01_MAINPY="backend/app/main.py"
if [ -f "$P01_NIXPACKS" ] && [ -f "$P01_MAINPY" ]; then
  if grep -qE -- '--workers[= ]*[2-9]' "$P01_NIXPACKS" && grep -q 'scheduler.start()' "$P01_MAINPY"; then
    print_fail "P0-1: multi-worker + scheduler in-process = crons duplicados"
    echo "    $P01_NIXPACKS arranca >1 worker mientras main.py corre APScheduler in-process."
    echo "    Sin locking distribuido → cada worker dispara los 24 crons (doble publicación · viola P2)."
    echo "    Fix: --workers 1, o extraer scheduler a proceso propio (DEBT-SCHEDULER-SPLIT)."
  else
    print_pass "Workers/scheduler coherentes (1 worker mientras scheduler corre in-process)"
  fi
else
  print_warn "nixpacks.toml o main.py no encontrado — check P0-1 omitido"
fi

# ─────────────────────────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  RESUMEN                                                      ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  Total checks:    $TOTAL"
echo -e "  ${GREEN}Pasados:${NC}         $((TOTAL - FAILURES))/$TOTAL"
[ "$WARNINGS" -gt 0 ] && echo -e "  ${YELLOW}Warnings:${NC}        $WARNINGS"
[ "$FAILURES" -gt 0 ] && echo -e "  ${RED}Fallidos:${NC}        $FAILURES"
echo ""

if [ "$FAILURES" -eq 0 ]; then
  echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║  ✓ TODO LIMPIO — push autorizado                              ║${NC}"
  echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
  exit 0
else
  echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${RED}║  ✗ PUSH BLOQUEADO — $FAILURES checks fallaron                            ║${NC}"
  echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
  echo ""
  echo "🐢💎 No velocity, only precision."
  echo ""
  echo "Soluciones:"
  echo "  · Lee DDD_REGLAS_OMEGA.md para cada regla violada"
  echo "  · Corrige y vuelve a correr este script"
  echo "  · NO hagas --no-verify · es solo para emergencias documentadas"
  exit 1
fi
