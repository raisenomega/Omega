# MIGRATION PLAN — OmegaRaisen → V3 Compliance

## Versión 1.0 · 17 mayo 2026 · Owner-approved

> Plan operacional para mover OmegaRaisen del estado actual ([deprecado]
> repos · multi-proveedor IA · sin enforcement) al estado V3 (raisenomega
> monorepo · solo Anthropic + Nano Banana + Veo 3.1 · DDD enforced).
>
> **Restricciones del owner (17 may 2026):**
> 1. Subir el código tal cual está primero — preservar UI, rutas, features.
> 2. Refactor a DDD progresivamente DESPUÉS de tener producción live.
> 3. Solo Anthropic para texto (Nano Banana + Veo 3.1 = excepciones).
> 4. DB nueva en blanco — sin migración de data de clientes viejos.
> 5. Sin Lovable — repo único `raisenomega/Omega` con Vercel + Railway.
> 6. Cero downtime crítico (no hay clientes pagando todavía).

---

# FASE 0 — DOCUMENTOS FUNDACIONALES  ✅ COMPLETADA HOY

**Duración:** ~3 horas · **Estado:** entregado en este turno

**Deliverables:**
- [X] SOURCE_OF_TRUTH.md
- [X] PRD_RECONSTRUIDO.md
- [X] CLAUDE.md (≤60L)
- [X] DDD_REGLAS_OMEGA.md
- [X] PROTOCOLO_SEGURIDAD_OMEGA.md
- [X] PROTOCOLO_IDENTIDAD_GIT_OMEGA.md
- [X] PLANTILLA_OMEGA_V3.md
- [X] MIGRATION_PLAN_OMEGA.md (este archivo)
- [X] README.md
- [X] scripts/validate-before-push.sh
- [X] scripts/verify-guardrails.sh
- [X] scripts/bootstrap.sh
- [X] .claude/hooks · .claude/agents · .claude/skills
- [X] supabase/migrations/{00001, 00002, 00003}.sql
- [X] backend/app/bc_cognition/domain/limits_omega.py

**Criterio de aceptación:**
Owner firma `SOURCE_OF_TRUTH.md` y `PRD_RECONSTRUIDO.md` (Sección 9).

---

# FASE 1 — INFRAESTRUCTURA NUEVA

**Duración:** 1-2 días · **Bloqueo:** firma owner Fase 0

## 1.1 — Crear repo GitHub nuevo

```bash
# En la cuenta corporativa raisenomega
gh auth login --hostname github.com --web --scopes "repo,admin:org"
gh auth switch --user raisenomega   # si tienes ambas configuradas

gh repo create raisenomega/Omega \
  --private \
  --description "OmegaRaisen v2 — Anthropic-only multi-tenant SaaS for social media automation" \
  --gitignore Python

cd "D:/Omega Master redes"   # ruta nueva en disco
git clone https://github.com/raisenomega/Omega.git .
```

## 1.2 — Configurar identidad git includeIf

Ver `PROTOCOLO_IDENTIDAD_GIT_OMEGA.md` sección "Setup dual". Resumen del setup real:

```bash
# ✅ YA HECHO en Fase 0 (arranque 17 may 2026):
# C:\Users\muscl\.gitconfig-omegamaster creado con:
#   user.name  = raisenomega
#   user.email = raisenagencypr@gmail.com
#   [init] defaultBranch = main
#   [core] autocrlf = input, ignorecase = false
#
# ~/.gitconfig tiene AL FINAL:
#   [includeIf "gitdir:D:/Omega Master redes/"]
#     path = C:/Users/muscl/.gitconfig-omegamaster
#   (el bloque de D:/Raisen Omega/ con .gitconfig-raisen NO se toca)

# Verificar que sigue activo:
cd "D:/Omega Master redes"
git config --get user.email   # debe retornar raisenagencypr@gmail.com
git config --get user.name    # debe retornar raisenomega
```

## 1.3 — Crear proyecto Supabase

```
URL  https://supabase.com/dashboard/new
Org  raisenomega (crear si no existe)
Plan Pro ($25/mes) — para pgvector + backups + branches
Name omega-prod
Region us-east-1 (más cercano a clientes y a Railway US-East)
DB password: generar 32+ chars con bw generate
```

**Guardar credenciales en password manager (NO en repo):**
- `SUPABASE_URL` = `https://rwlnihoqhxwpbehibgxu.supabase.co` (ya creado según el owner)
- `SUPABASE_ANON_KEY` (público — frontend)
- `SUPABASE_SERVICE_ROLE_KEY` (secreto — solo backend Railway)
- `DATABASE_URL` (pooler URL — para SQLAlchemy)
- `SUPABASE_DB_PASSWORD` (para CLI)

## 1.4 — Habilitar extensions y aplicar migraciones

En Supabase SQL Editor:

```sql
-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";          -- pgvector V3 obligatorio
CREATE EXTENSION IF NOT EXISTS "pg_cron";         -- futuro auto-evaluación
```

Luego ejecutar en orden:
```
supabase/migrations/00001_initial_consolidated.sql
supabase/migrations/00002_agent_memory_pgvector.sql
supabase/migrations/00003_rls_complete.sql
```

Verificar con query post-migración:

```sql
-- Toda tabla con identificadores debe tener RLS:
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND rowsecurity = false;
-- Esperado: 0 filas
```

## 1.5 — Crear proyecto Vercel

```
https://vercel.com/new
Team:        raisenomega (crear)
Import:      github.com/raisenomega/Omega (root del repo)
Framework:   Vite
Build cmd:   npm run build
Output:      dist
Install:     npm install
Root dir:    ./ (raíz; la app es Vite-only frontend)
```

**Variables de entorno en Vercel (Production + Preview):**
```
VITE_SUPABASE_URL              https://rwlnihoqhxwpbehibgxu.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY  [anon key]
VITE_API_URL                   https://omega-backend.up.railway.app/api/v1
VITE_APP_ENV                   production
```

**Custom domain:** apuntar `r-omega.agency` a Vercel.

## 1.6 — Crear proyecto Railway

```
https://railway.app/new
Source:      GitHub repo raisenomega/Omega
Root dir:    backend/
Build:       nixpacks (auto-detecta backend/nixpacks.toml)
Start cmd:   uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Variables de entorno en Railway:**
```
ENVIRONMENT                  production
DEBUG                        false
SECRET_KEY                   [generar 64 chars]
JWT_SECRET_KEY               [generar 64 chars]
JWT_ALGORITHM                HS256

SUPABASE_URL                 https://rwlnihoqhxwpbehibgxu.supabase.co
SUPABASE_ANON_KEY            [anon key]
SUPABASE_SERVICE_ROLE_KEY    [service role — secreto]
DATABASE_URL                 [pooler url]

ANTHROPIC_API_KEY            [sk-ant-...]
GEMINI_API_KEY               [google ai key — para Nano Banana + Veo 3.1]

STRIPE_SECRET_KEY            [sk_live_...]
STRIPE_WEBHOOK_SECRET        [whsec_...]
STRIPE_PRICE_BASIC           [price_...]
STRIPE_PRICE_PRO             [price_...]
STRIPE_PRICE_ENTERPRISE      [price_...]

BRAVE_API_KEY                [brave search]
LANGFUSE_PUBLIC_KEY          [pk-...] (post-integración)
LANGFUSE_SECRET_KEY          [sk-...] (post-integración)

BACKEND_CORS_ORIGINS         https://r-omega.agency,https://www.r-omega.agency,https://omega.vercel.app
```

**Custom domain:** `omega-backend.up.railway.app` (default) o subdominio propio.

## 1.7 — Rotar TODAS las API keys

Asumir que cualquier key visible en repos viejos está comprometida:

```
[ ] Anthropic     → revocar key vieja · crear key nueva en console.anthropic.com
[ ] Google Gemini → crear key nueva en aistudio.google.com (incluye Nano Banana + Veo)
[ ] Stripe        → rotar Restricted Keys + webhook secret
[ ] Brave Search  → revocar + recrear en search.brave.com/dashboard
[ ] Supabase      → keys nuevas (vienen del proyecto nuevo, no requiere rotar)
[ ] OpenAI        → REVOCAR PERMANENTEMENTE (ya no se usa)
[ ] Groq          → REVOCAR PERMANENTEMENTE
[ ] DeepSeek      → REVOCAR PERMANENTEMENTE
[ ] Runway        → REVOCAR PERMANENTEMENTE
[ ] FAL           → REVOCAR PERMANENTEMENTE
[ ] Tavily        → REVOCAR (Brave Search lo reemplazó)
```

**Criterio de aceptación Fase 1:**
- Repo `raisenomega/Omega` existe vacío
- Supabase live con extensions + migraciones aplicadas
- Vercel deploy de "Hello World" funciona
- Railway deploy de "Hello World FastAPI" funciona
- Owner confirma keys rotadas y guardadas

---

# FASE 2 — LIFT & SHIFT "TAL CUAL ESTÁ" + SWAP DE PROVEEDORES IMAGEN/VIDEO

**Duración:** 5-7 días · **Bloqueo:** Fase 1 verde

> **Filosofía de esta fase:** preservar 100% de funcionalidad, UI, rutas,
> flujos. Solo se modifican: (a) variables de conexión a nueva infra,
> (b) las llamadas a DALL-E 3 → Nano Banana, (c) las llamadas Runway/FAL → Veo 3.1.
> TODO LO DEMÁS queda igual. OpenAI/Groq/DeepSeek se REMUEVEN del codebase
> en esta fase porque su refactor mínimo es ese: eliminar imports y rutas
> que las usan. Si una función dependía exclusivamente de OpenAI text gen,
> se desactiva con feature flag temporal (no se rompe la app).

## 2.1 — Migrar código backend

```bash
# Desde el zip existente, copiar al repo nuevo
cp -r "extracted/Master redes/backend/" D:/Omega Master redes/backend/

# Limpiar node_modules y venv si vinieron
rm -rf D:/Omega Master redes/backend/venv
rm -rf D:/Omega Master redes/backend/__pycache__

# Reemplazar config.py: solo Anthropic + Gemini, sin OpenAI
# (ver Sección 2.4 abajo)

# Reemplazar requirements.txt con la versión limpia
cp output/backend/requirements.txt D:/Omega Master redes/backend/requirements.txt
```

## 2.2 — Migrar código frontend

```bash
# Necesitas clonar r-omegaagency (último estado en Lovable) para tener el
# frontend completo y actualizado. El src/ del zip es STALE.
gh repo clone repo frontend anterior (deprecado) tmp-frontend
cp -r tmp-frontend/src D:/Omega Master redes/src
cp tmp-frontend/{package.json,vite.config.ts,tsconfig*.json,index.html,components.json,tailwind.config.ts,postcss.config.js,eslint.config.js} D:/Omega Master redes/
rm -rf tmp-frontend
```

Si **no tienes acceso a r-omegaagency** (Lovable cerrado, etc.):

```bash
# Usar el src/ del zip como base y reportar al owner que faltan
# las features añadidas en Lovable post-último-pull. Esto puede
# significar pérdida de funcionalidad. Owner debe confirmar.
cp -r "extracted/Master redes/src" D:/Omega Master redes/src
cp "extracted/Master redes/"{package.json,vite.config.ts,...} D:/Omega Master redes/
```

## 2.3 — Migraciones SQL al Supabase nuevo

```bash
# Instalar Supabase CLI
npm install -g supabase

# Vincular el proyecto local al Supabase nuevo
cd "D:/Omega Master redes"
supabase link --project-ref rwlnihoqhxwpbehibgxu

# Aplicar migraciones consolidadas
supabase db push
```

**Las 25 migraciones viejas (3 directorios distintos) se consolidan en:**
- `00001_initial_consolidated.sql` — toda la estructura actual unificada
- `00002_agent_memory_pgvector.sql` — V3 nuevo (no existía)
- `00003_rls_complete.sql` — cierra los gaps de RLS detectados

## 2.4 — Hot-swap de proveedores: DALL-E 3 → Nano Banana

Archivos a modificar (manteniendo signature + comportamiento):

```
backend/app/agents/content_creator/image_generation.py
  ANTES: from app.infrastructure.ai.openai_service import openai_service
         urls = await openai_service.generate_image(...)
  DESPUÉS:
         from app.bc_cognition.infrastructure.nano_banana_adapter import nano_banana
         urls = await nano_banana.generate(prompt, aspect_ratio, ...)

backend/app/api/routes/content_lab/handlers/generate_image.py
  Mismo patrón. Signature externa no cambia.
```

## 2.5 — Hot-swap: Runway/FAL → Veo 3.1

```
backend/app/agents/runway_agent.py        → eliminar
backend/app/agents/fal_video_agent.py     → eliminar
backend/app/agents/video_production_agent.py
  Reemplazar lógica interna por veo3_adapter
  Signature externa intacta
backend/app/api/routes/content_lab/handlers/generate_video_fal.py → eliminar
backend/app/api/routes/content_lab/handlers/generate_video.py
  Apuntar a veo3_adapter
```

## 2.6 — Eliminar imports OpenAI/Groq/DeepSeek (cumple I1)

```
backend/app/infrastructure/ai/openai_service.py                       → ELIMINAR
backend/app/infrastructure/ai/providers/openai_provider.py            → ELIMINAR
backend/app/infrastructure/ai/providers/groq_provider.py              → ELIMINAR
backend/app/infrastructure/ai/providers/deepseek_provider.py          → ELIMINAR
backend/app/infrastructure/ai/providers/gemini_provider.py            → ELIMINAR (no era de imagen)
backend/app/agents/groq_agent.py                                       → ELIMINAR

# Reemplazar todas las llamadas a estos servicios por anthropic_adapter
# Si una función dependía exclusivamente: marcar con feature flag temporal
```

Llamadas a reemplazar (basado en grep):

```python
# ANTES (varios archivos):
from app.infrastructure.ai.openai_service import openai_service
caption = await openai_service.generate_text(model="gpt-4o", ...)

# DESPUÉS:
from app.bc_cognition.infrastructure.anthropic_adapter import claude
caption = await claude.generate(
    model_tier="sonnet",   # routing automático
    system=BRAND_VOICE_SYSTEM_PROMPT,
    messages=[...],
)
```

## 2.7 — Deploy + smoke test

```bash
# Verify cumple I1
bash scripts/validate-before-push.sh   # debe pasar 9/9

git add .
git commit -m "feat: bootstrap OmegaRaisen V2 — Anthropic-only + Nano Banana + Veo 3.1"
git push -u origin main

# Vercel auto-deploya frontend
# Railway auto-deploya backend
# Verificar:
curl https://omega-backend.up.railway.app/health
# {"status":"healthy","version":"2.0.0","agents":"X/X","environment":"production"}

# Smoke test
curl -X POST https://omega-backend.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@raisenomega.com","password":"Test1234!","name":"Test"}'
```

**Criterio de aceptación Fase 2:**
- `validate-before-push.sh` pasa 9/9 (incluido I1)
- `/health` retorna 200
- Login funciona con usuario nuevo en Supabase nuevo
- Una generación de texto vía Anthropic funciona
- Una generación de imagen vía Nano Banana funciona
- Una generación de video vía Veo 3.1 funciona
- Frontend Vercel carga sin errores de consola
- Cero referencias a openai/groq/deepseek en código (grep limpio)

---

# FASE 3 — REFACTOR A DDD PROGRESIVO

**Duración:** 4-6 semanas · **Bloqueo:** Fase 2 verde · Sistema live

> **Filosofía:** ya está produciendo. Ahora se refactoriza POR
> BOUNDED CONTEXT, uno a la vez, con SENTINEL verde antes y después
> de cada PR. Nunca se mezclan contextos en un mismo PR.

## 3.1 — Crear bc_cognition completo (Semana 1)

```
backend/app/bc_cognition/
├── domain/
│   ├── __init__.py
│   ├── persona_nova.py            ← system prompt CEO (SHA1 verificado)
│   ├── persona_atlas.py           ← system prompt Marketing Director
│   ├── persona_luna.py            ← system prompt Tech Director
│   ├── limits_omega.py            ← guardrails (SHA1 baseline)
│   ├── conviction.py              ← P3: confidence ≥ 7
│   ├── episodic_memory.py         ← tipos de memoria
│   └── routing_table.py           ← Haiku/Sonnet/Opus por agente
├── application/
│   ├── __init__.py
│   ├── use_agent.py
│   ├── context_builder.py         ← contexto ≤2000 tokens
│   └── memory_query.py
└── infrastructure/
    ├── __init__.py
    ├── anthropic_adapter.py       ← ÚNICO entry point Claude
    ├── nano_banana_adapter.py     ← ÚNICO entry point Gemini Image
    ├── veo3_adapter.py            ← ÚNICO entry point Veo Video
    ├── memory_repository.py       ← persistencia agent_memory
    └── langfuse_observer.py       ← observabilidad LLM
```

## 3.2 — Refactor por Bounded Context (Semanas 2-5)

Orden por menor riesgo → mayor riesgo:

```
Semana 2:  bc-cognition (ya creado, solo conectar todo)
Semana 3:  bc-04-analytics  (lectura intensiva, bajo riesgo)
Semana 4:  bc-06-sentinel + bc-07-oracle (sistemas autónomos)
Semana 5:  bc-02-content-lab (donde está el corazón)
Semana 6:  bc-03-calendar + bc-05-resellers (multi-tenant)
Semana 7:  bc-01-clients (la última — máximo cuidado RLS)
```

Cada semana:
1. Lunes: planificar PR del bounded context, screenshot del SENTINEL pre-cambio
2. Mar-Jue: refactor, mantener tests verdes, commit por archivo
3. Vie: SENTINEL post-cambio, validar score ≥ 95, merge

## 3.3 — Split de archivos >75L (continuo)

Aplicar regla `R-LINES-001` progresivamente. 202 archivos hoy. Target: 0 archivos >100L.

Archivos prioritarios (>250L):
```
backend/app/agents/trend_hunter_agent.py        316L
backend/app/agents/analytics_agent.py           313L
backend/app/agents/engagement_agent.py          306L
backend/app/agents/scheduling_agent.py          301L
backend/app/agents/crisis_manager_agent.py      298L
backend/app/agents/brand_voice_agent.py         289L
```

**Criterio de aceptación Fase 3:**
- 7/7 bounded contexts refactorizados
- 0 archivos backend >100L
- Tests cobertura ≥ 60% en domain/ y application/
- SENTINEL score ≥ 95 sostenido durante el periodo

---

# FASE 4 — CLAUDE CODE STACK + AUTO-EVOLUCIÓN

**Duración:** 1-2 semanas · **Bloqueo:** Fase 3 verde

## 4.1 — Activar Claude Code stack

```bash
# Ya están los archivos en .claude/ del bootstrap, ahora se activan:
claude mcp add supabase --env SUPABASE_URL=$SUPABASE_URL --env SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_ROLE_KEY
claude mcp add github --env GITHUB_TOKEN=$GITHUB_PAT
claude mcp add context7
claude mcp add memory

# Verify
claude mcp list   # debe mostrar 4
```

## 4.2 — Promptfoo baseline para 5 agentes core

```yaml
# promptfoo.yaml
providers:
  - id: anthropic:claude-sonnet-4-6
    config:
      apiKey: $ANTHROPIC_API_KEY

prompts:
  - file://bc_cognition/domain/persona_nova.py
  - file://bc_cognition/domain/persona_atlas.py

tests:
  - description: "Content Creator respeta brand voice"
    vars:
      brand_voice: "profesional, conciso, sin emojis"
      tema: "lanzamiento producto"
    assert:
      - type: contains-any
        value: ["lanzamiento", "presentamos"]
      - type: not-contains-any
        value: ["🎉", "🚀", "amigos"]
```

## 4.3 — Integrar Langfuse

```python
# backend/app/bc_cognition/infrastructure/anthropic_adapter.py
from langfuse.decorators import observe

@observe(name="claude_messages_create")
async def generate(model_tier, system, messages):
    response = await client.messages.create(...)
    return response
```

## 4.4 — Bias Detection semanal

Subagente que corre cada domingo 23:59 AST:
- Lee últimos 500 episodios de agent_memory
- Detecta patrones (overconfidence en X, underconfidence en Y, drift en brand voice)
- Genera reporte markdown
- Notifica owner vía NOVA

**Criterio de aceptación Fase 4:**
- 4 MCPs activos
- Promptfoo baseline con ≥10 casos
- Langfuse capturando 100% de llamadas
- Reporte bias-detection generado y revisado

---

# RIESGOS Y MITIGACIONES

```
RIESGO                                     MITIGACIÓN
──────────────────────────────────────     ─────────────────────────────────────
R1: Frontend de Lovable inaccesible       Fallback: src/ del zip + reconstrucción
                                          manual con owner aprobando cada feature
R2: Migración Phase 2 rompe función X     Cada función tiene smoke test en 2.7.
                                          Si falla: rollback inmediato (git revert)
R3: Costo Anthropic sube vs OpenAI         Routing Haiku para tareas simples.
                                          Monitoreo per-cliente con limit $5/día
R4: Nano Banana watermark SynthID          Documentar en TOS del cliente. Es
                                          requisito legal de Google, no negociable.
R5: Veo 3.1 latencia (8s video ~30s API)   UI con polling. Background job pattern.
R6: 8 cron workers nuevos en Railway       Verificar /api/v1/system/cron-status
                                          post-deploy. Si <8: re-deploy.
R7: Migración Supabase pierde data         No aplica — owner aprobó "partir en
                                          blanco". Reseller test = primer usuario.
R8: SHA1 limits_omega.py rota              Esto es feature, no bug. Bloquea deploys
                                          hasta firma del owner del cambio.
```

---

# TIMELINE CONSOLIDADO

```
DÍA   FASE   ENTREGABLE                              OWNER ACTION
───   ────   ──────────────────────────────────     ────────────────────────
0     0      Documentos fundacionales (HOY)          Firmar SOT + PRD
1     1      Repos + Supabase + Vercel + Railway    Aprobar keys rotadas
2     1      Identidad git + secrets en password mgr
3     2      Backend code migrado a repo nuevo      Smoke test backend
4     2      Frontend code migrado                  Smoke test frontend
5     2      Hot-swap DALL-E → Nano Banana          Aprobar imagen test
6     2      Hot-swap Runway/FAL → Veo 3.1          Aprobar video test
7     2      Eliminar OpenAI/Groq/DeepSeek          validate-before-push 9/9
8     2      Deploy producción + smoke E2E          GO/NO-GO Fase 3
9-15  3      bc_cognition + bc-04-analytics
16-22 3      bc-06-sentinel + bc-07-oracle
23-29 3      bc-02-content-lab
30-36 3      bc-03-calendar + bc-05-resellers
37-43 3      bc-01-clients (último, máxima atención)
44-50 4      Claude Code stack + Promptfoo + Langfuse
51+         Auto-evolución activa · operación normal
```

---

# CRITERIOS DE ÉXITO GLOBALES

Al final de Fase 4 (~día 50):

```
[ ] SENTINEL score 100/100 sostenido 7 días
[ ] validate-before-push.sh pasa 12/12 (incluye los nuevos X1-X5)
[ ] Cero referencias a openai/groq/deepseek/runwayml/fal_client en código
[ ] Tests cobertura ≥ 60% en domain/ y application/
[ ] 0 archivos backend >100L (warning >75L OK temporal)
[ ] Promptfoo baseline con ≥ 30 casos · regresión < 5%
[ ] Langfuse captura 100% de llamadas Claude
[ ] agent_memory tiene ≥ 100 episodios cerrados (was_correct evaluado)
[ ] Identidad git de TODOS los commits desde Fase 1 = raisenomega
[ ] Owner firma "OmegaRaisen V2 producción ready"
```

---

```
MIGRATION_PLAN_OMEGA.md
Versión 1.0 · 17 mayo 2026
Próxima revisión: al cerrar Fase 1 (verificar criterios + ajustar timing Fase 2)
Estado: documento vivo — actualizar tras cada cierre de fase
```
