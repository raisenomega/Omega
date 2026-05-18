# 🗺️ ÍNDICE DEL PROYECTO — OmegaRaisen
## Mapa completo · Orden de lectura · Alineación de Claude Code
### Versión 1.0 · 17 mayo 2026

> **Este documento es la PRIMERA cosa que Claude Code lee al abrir
> `D:\Omega Master redes\`.** Define:
> 1. Estado actual del proyecto en 30 segundos
> 2. Orden exacto de lectura por tier (qué SIEMPRE · qué SEGÚN scope · qué REFERENCIA)
> 3. Mapa de cada archivo con su rol y ubicación
> 4. Gates de readiness — "esta sesión NO puede empezar hasta…"
> 5. Protocolo de primer arranque vs sesión recurrente
>
> **Sin leer este índice primero: no procedas con ninguna tarea técnica.**

---

## SECCIÓN 1 — ESTADO ACTUAL EN 30 SEGUNDOS

```
PROYECTO        OmegaRaisen ("Master Redes") · Raisen Agency
DUEÑO           Ibrain Raisen
REPO            github.com/raisenomega/Omega   (a crear en Fase 1)
RUTA LOCAL      D:\Omega Master redes\         ← AQUÍ ESTAMOS
SUPABASE        rwlnihoqhxwpbehibgxu.supabase.co (creado · sin migraciones aún)

FASE ACTUAL     0 — Bootstrap V3 documentado y entregado
PRÓXIMA FASE    1 — Crear infraestructura nueva (1-2 días)

STACK           Python 3.11 + FastAPI · Vite + React + TS · Supabase + pgvector
IA              Anthropic Claude (único texto) · Nano Banana (imagen) · Veo 3.1 (video)
ELIMINADOS      OpenAI · Groq · DeepSeek · Runway · FAL · DALL-E 3 · Tavily

DECISIONES OWNER (17 may 2026)
  · Solo Anthropic estricto (I1) + 2 excepciones Google documentadas
  · Frontend "tal cual está" en Fase 2, refactor a DDD en Fase 3
  · Supabase nuevo en blanco · sin migración de data antigua
  · Repo único raisenomega/Omega · sin Lovable · Vercel + Railway
```

---

## SECCIÓN 2 — ORDEN DE LECTURA OBLIGATORIO

### 🔴 TIER 1 — LECTURA SIEMPRE (3 archivos · ~5 min)

Antes de cualquier acción técnica en CUALQUIER sesión:

```
1. INDICE_PROYECTO.md           ← este documento · ya lo estás leyendo
2. IDENTIDAD_GIT_CRITICA.md     ← bloqueante · 4 verificaciones git
3. CLAUDE.md                    ← constitución (60L) · reglas non-negotiable
4. SOURCE_OF_TRUTH.md           ← qué existe · qué no · 11 deudas técnicas
```

**Sin estos 4 leídos:** no escribir código, no commitear, no proponer cambios.

### 🟠 TIER 2 — LECTURA SEGÚN SCOPE DE LA SESIÓN

Si vas a tocar **arquitectura / agentes / cognición IA:**
```
5. DDD_REGLAS_OMEGA.md          contrato técnico (60+ reglas)
6. BC_COGNITION_OMEGA.md        arquitectura del cerebro IA (37 agentes)
```

Si vas a tocar **MCPs / integraciones externas:**
```
7. MCP_ARSENAL_OMEGA.md          catálogo de conectores · roadmap por fase
```

Si vas a tocar **deploy / infraestructura / migración:**
```
8. MIGRATION_PLAN_OMEGA.md       plan operacional 5 fases con timeline
```

Si vas a tocar **seguridad / RLS / auth / secrets:**
```
9. PROTOCOLO_SEGURIDAD_OMEGA.md  defensa CIA-level · 11 capas
```

Si vas a tocar **identidad git / collaboradores / signing:**
```
10. PROTOCOLO_IDENTIDAD_GIT_OMEGA.md  setup includeIf · troubleshooting
```

Si vas a tocar **base de datos / tablas / RLS:**
```
11. supabase/migrations/00001_initial_consolidated.sql
12. supabase/migrations/00002_agent_memory_pgvector.sql
13. supabase/migrations/00003_rls_verification_seed.sql
```

### 🟢 TIER 3 — REFERENCIA SEGÚN NECESITES

Consulta solo si una tarea específica lo requiere:

```
14. PRD_RECONSTRUIDO.md          visión del producto · las 4 preguntas P1-P4
15. PLANTILLA_OMEGA_V3.md        plantilla universal V3 adaptada
16. README.md                    onboarding general (≈ portada del repo)
```

---

## SECCIÓN 3 — ESTRUCTURA COMPLETA DE `D:\Omega Master redes\`

```
D:\Omega Master redes\
│
├── 📄 DOCUMENTOS RECTORES (raíz · todos .md)
│   ├── INDICE_PROYECTO.md              ⭐ ESTE archivo · mapa maestro
│   ├── IDENTIDAD_GIT_CRITICA.md        ⚠️ bloqueante git
│   ├── CLAUDE.md                       constitución 60L
│   ├── SOURCE_OF_TRUTH.md              estado verificado · deudas
│   ├── PRD_RECONSTRUIDO.md             visión del producto
│   ├── DDD_REGLAS_OMEGA.md             contrato técnico inviolable
│   ├── BC_COGNITION_OMEGA.md           arquitectura cerebro IA
│   ├── MCP_ARSENAL_OMEGA.md            catálogo conectores
│   ├── MIGRATION_PLAN_OMEGA.md         plan 5 fases
│   ├── PROTOCOLO_SEGURIDAD_OMEGA.md    defensa CIA-level
│   ├── PROTOCOLO_IDENTIDAD_GIT_OMEGA.md   setup includeIf detallado
│   ├── PLANTILLA_OMEGA_V3.md           plantilla universal adaptada
│   └── README.md                       portada
│
├── ⚙️ CONFIGURACIÓN (raíz)
│   ├── .env.example                    plantilla de variables · NO commitear .env real
│   ├── .gitignore
│   ├── tsconfig.json                   TypeScript strict V3 + 9 flags + aliases bc-*
│   └── vercel.json                     headers de seguridad + framework Vite
│
├── 🐍 BACKEND (Python 3.11 + FastAPI)
│   └── backend\
│       ├── nixpacks.toml               config Railway
│       ├── requirements.txt            Anthropic + google-genai · sin OpenAI/Groq/etc.
│       └── app\
│           ├── __init__.py
│           ├── (resto del backend legacy — refactor progresivo Fase 3)
│           └── bc_cognition\           ⭐ EL CEREBRO
│               ├── __init__.py
│               ├── domain\             cero imports externos · capa pura
│               │   ├── __init__.py
│               │   ├── limits_omega.py       ⚠️ inmutable · SHA1 ee472c1d...
│               │   ├── persona_nova.py       system prompt CEO Agent · P1-P5
│               │   └── routing_table.py      37 agentes → Haiku/Sonnet/Opus
│               ├── application\
│               │   └── __init__.py     (use cases pendientes Fase 3)
│               └── infrastructure\     ÚNICA capa que toca SDKs externos
│                   ├── __init__.py
│                   ├── anthropic_adapter.py        ÚNICO entry Claude
│                   ├── _anthropic_types.py         tipos + pricing
│                   ├── nano_banana_adapter.py      ÚNICO entry Gemini Image (I1 excepción)
│                   ├── _nano_banana_types.py
│                   ├── veo3_adapter.py             ÚNICO entry Veo 3.1 (I1 excepción)
│                   └── _veo3_types.py
│
├── ⚛️ FRONTEND (Vite + React + TypeScript)
│   └── src\                            (a copiar desde repo anterior Lovable en Fase 2)
│
├── 🐘 BASE DE DATOS (Supabase migrations)
│   └── supabase\
│       └── migrations\
│           ├── 00001_initial_consolidated.sql      17 tablas con RLS completo
│           ├── 00002_agent_memory_pgvector.sql     agent_memory + vector(1536) + ivfflat
│           └── 00003_rls_verification_seed.sql    verificación RLS + seed 37 agentes
│
├── 🛠️ SCRIPTS (enforcement + setup)
│   └── scripts\
│       ├── validate-before-push.sh     10 checks zero-tolerance (Check 0 = identidad git)
│       ├── verify-guardrails.sh        SHA1 limits_omega.py · modo --update
│       ├── bootstrap.sh                setup inicial idempotente · 8 pasos
│       └── guardrails-sha1.txt         baseline: ee472c1d398afc46e34ac4bd42d349b0bf6e9649
│
└── 🤖 CLAUDE CODE STACK
    └── .claude\
        ├── settings.json               hooks + agents + skills + alwaysReadFirst
        ├── hooks\
        │   ├── protect-guardrails.py   PreToolUse · bloquea modif a archivos protegidos
        │   ├── check-file-length.py    PostToolUse · warn >75L · error >100L
        │   └── verify-on-stop.sh       Stop · verifica SHA1 + tests pre-cierre
        ├── agents\
        │   ├── auditor.md              Opus read-only · análisis arquitectónico
        │   ├── memory-writer.md        Haiku · persiste decisiones en agent_memory
        │   └── context-checker.md      Haiku · verifica bootstrap de sesión
        └── skills\
            ├── iniciar-fase\SKILL.md   procedimiento al empezar fase
            ├── cerrar-ciclo\SKILL.md   procedimiento al cerrar fase
            ├── auditoria\SKILL.md      lanzar auditoría sobre scope
            └── registrar-deuda\SKILL.md   documentar deuda nueva
```

---

## SECCIÓN 4 — MAPA "SI NECESITAS X, VAS A Y"

```
TAREA                                     → ARCHIVO(S) DONDE BUSCAR
─────────────────────────────────────────   ─────────────────────────────────────────
"¿Cuál es mi identidad git aquí?"          IDENTIDAD_GIT_CRITICA.md §1
"¿Cómo configuro includeIf?"               PROTOCOLO_IDENTIDAD_GIT_OMEGA.md §2
"¿Qué reglas no puedo violar nunca?"        DDD_REGLAS_OMEGA.md (P1-P5 + reglas A-X)
"¿Qué modelo Claude usa el agente X?"      backend/.../routing_table.py + DDD I2
"¿Dónde modifico los guardrails?"          backend/.../limits_omega.py
                                            ⚠️ requiere test + aprobación owner + SHA1 rotation
"¿Cuántos agentes hay y su estado?"         BC_COGNITION_OMEGA.md §4
"¿Cómo añado un MCP nuevo?"                 MCP_ARSENAL_OMEGA.md (estado · roadmap)
"¿Qué hago primero para deploy?"            MIGRATION_PLAN_OMEGA.md §Fase 1
"¿Qué tabla necesito crear?"                supabase/migrations/00001_*.sql
"¿Por qué la RLS rompe esta query?"         PROTOCOLO_SEGURIDAD_OMEGA.md §Capa 3
"¿Qué hace el pre-push hook?"               scripts/validate-before-push.sh (10 checks)
"¿Por qué se eliminó OpenAI?"               DDD_REGLAS_OMEGA.md regla I1 + decisión owner
"¿Por qué Nano Banana y no DALL-E?"         MCP_ARSENAL_OMEGA.md §3.1 (5 razones)
"¿Qué tests debo escribir?"                 DDD_REGLAS_OMEGA.md categoría T + BC_COGNITION §8 DoD
"¿Qué deuda hay registrada?"                SOURCE_OF_TRUTH.md §6 (DEBT-001 a DEBT-011)
"¿Cómo registro una deuda nueva?"           .claude/skills/registrar-deuda/SKILL.md
"¿Cómo cierro una fase de trabajo?"         .claude/skills/cerrar-ciclo/SKILL.md
"¿Cómo lanzo una auditoría arquitectónica?" .claude/skills/auditoria/SKILL.md
"¿Qué es NOVA / SENTINEL / ORACLE?"         BC_COGNITION_OMEGA.md §4.2 + PRD §3
"¿Cuál es la métrica principal de éxito?"   SOURCE_OF_TRUTH.md §5 (SENTINEL ≥ 95)
"¿Cuándo activo Langfuse?"                  MCP_ARSENAL_OMEGA.md §6.1 (Fase 4)
"¿Cuándo activo Meta API?"                  MCP_ARSENAL_OMEGA.md §2.1 (Fase 2-3)
```

---

## SECCIÓN 5 — GATES DE READINESS

Esta sesión **NO puede empezar a trabajar** hasta que estos 6 ítems estén ✅:

```
[ ] 1. ESTOY EN LA RUTA CORRECTA
       pwd retorna  /d/Omega Master redes  (Git Bash)
       o            D:\Omega Master redes  (PowerShell)

[ ] 2. IDENTIDAD GIT VERIFICADA (4 condiciones · IDENTIDAD_GIT_CRITICA §2)
       git config --get user.email    → raisenagencypr@gmail.com
       git config --get user.name     → raisenomega
       git remote -v                  → https://github.com/raisenomega/Omega.git
       pwd                            → D:\Omega Master redes\

[ ] 3. LEÍ TIER 1 COMPLETO
       INDICE_PROYECTO.md (este)  ·  IDENTIDAD_GIT_CRITICA  ·  CLAUDE.md  ·  SOURCE_OF_TRUTH

[ ] 4. LEÍ TIER 2 SEGÚN MI SCOPE DE HOY
       Si voy a tocar bc_cognition → DDD_REGLAS + BC_COGNITION_OMEGA
       Si voy a tocar MCPs         → MCP_ARSENAL_OMEGA
       (etc. según mapa Sección 2)

[ ] 5. CONOZCO EL ESTADO DE DEUDA TÉCNICA
       SOURCE_OF_TRUTH §6 → 11 deudas conocidas · 344h estimadas
       Soy consciente de cuáles tocan mi scope de hoy

[ ] 6. DECLARÉ INTENCIÓN AL OWNER
       Antes de la primera edición:
        · Scope de la sesión (qué SÍ · qué NO)
        · Archivos a crear/modificar
        · Reglas DDD aplicables
        · Riesgos identificados
        · Criterio de éxito
       Espero confirmación antes de proceder.
```

**Cualquier ítem en ❌:** se reporta al owner y se pausa.

---

## SECCIÓN 6 — PROTOCOLO DE PRIMER ARRANQUE

### Si esta es la PRIMERA sesión en este repo (jamás se ha trabajado aquí):

```bash
# Paso 1 — Confirma ubicación
cd "D:/Omega Master redes"
pwd                          # → /d/Omega Master redes
ls -la                       # debe ver los .md, backend/, scripts/, supabase/, .claude/

# Paso 2 — Configura identidad git (PROTOCOLO_IDENTIDAD_GIT_OMEGA "Setup dual")
# YA HECHO en el arranque de Fase 0: .gitconfig-omegamaster creado
# Verifica que sigue activo:
git config --get user.email     # → raisenagencypr@gmail.com

# Paso 3 — Ejecuta bootstrap idempotente
bash scripts/bootstrap.sh
# Verificará: prerequisitos · identidad · .env · npm install · pip install
#             permisos de scripts · git hooks · SHA1 baseline

# Paso 4 — Edita .env con tus credenciales reales (NO commitear)
cp .env.example .env
# Editar con: ANTHROPIC_API_KEY · GEMINI_API_KEY · SUPABASE_* · STRIPE_* · etc.

# Paso 5 — Inicializa el repo git con remote correcto
git init                                     # si no existe .git/
git remote add origin https://github.com/raisenomega/Omega.git
# (o si el repo ya existe en GitHub: git clone desde D:/ y renombra)

# Paso 6 — Aplica las 3 migraciones SQL al Supabase nuevo
supabase link --project-ref rwlnihoqhxwpbehibgxu
supabase db push
# Verifica que las 17 tablas tengan RLS = true

# Paso 7 — Verifica los hooks
bash scripts/verify-guardrails.sh           # debe ✓ SHA1 OK
bash scripts/validate-before-push.sh        # 10/10 (tests pueden fallar inicialmente)

# Paso 8 — Listo. Reportar al owner: "Bootstrap completo. Procedo con Fase 1."
```

### Si esta es una sesión RECURRENTE (ya hay commits):

```bash
# Paso 1 — Confirma identidad
cd "D:/Omega Master redes"
git config --get user.email     # → raisenagencypr@gmail.com (debe match)

# Paso 2 — Sincroniza
git fetch origin
git status                       # ver estado actual
git log --oneline -10            # últimos 10 commits

# Paso 3 — Lee últimos episodios de agent_memory (si Supabase MCP activo)
# Memory MCP debe estar activo · sino: re-explicar contexto

# Paso 4 — Lee Tier 1 (siempre) + Tier 2 según scope

# Paso 5 — Declara intención · espera confirmación owner
```

---

## SECCIÓN 7 — INTEGRACIÓN CON CLAUDE CODE

`.claude/settings.json` debe tener:

```json
{
  "behavior": {
    "alwaysReadFirst": [
      "INDICE_PROYECTO.md",
      "IDENTIDAD_GIT_CRITICA.md",
      "CLAUDE.md",
      "SOURCE_OF_TRUTH.md"
    ],
    "planModeThreshold": 3
  }
}
```

`CLAUDE.md` referencia este documento como punto de entrada.

`.claude/skills/iniciar-fase/SKILL.md` invoca este documento como Paso 1.

---

## SECCIÓN 8 — ANTI-PATRONES A EVITAR

```
❌ "Voy a abrir un archivo y empezar a editar sin leer INDICE_PROYECTO"
   Resultado: rompes una regla DDD que no conocías
   Corrección: leer Tier 1 + Tier 2 según scope ANTES de editar

❌ "Ya leí estos docs hace 2 días, me los sé"
   Resultado: el estado del proyecto pudo cambiar (commits, decisiones)
   Corrección: SOURCE_OF_TRUTH siempre se relee · es snapshot vigente

❌ "Voy a saltar Memory MCP esta sesión, no la necesito"
   Resultado: repites errores documentados de sesiones anteriores
   Corrección: Memory MCP es CRÍTICO entre sesiones (MCP_ARSENAL §1.3)

❌ "El owner ya me dio aprobación verbal, no necesito declarar intención"
   Resultado: scope creep silencioso, decisiones que no están en log
   Corrección: declaración escrita en chat antes de primera edición

❌ "Esta tarea es pequeña, no aplica el gate 6"
   Resultado: las tareas pequeñas son las que cambian el SHA1
   Corrección: el gate aplica · 30 segundos de declaración > 3 días de rollback
```

---

## SECCIÓN 9 — CHECKLIST FINAL ANTES DE PROCEDER

Antes de tu primera edición en esta sesión:

```
[ ] He leído INDICE_PROYECTO.md (este documento)
[ ] He verificado identidad git con 4 condiciones
[ ] He leído CLAUDE.md · sé qué NO debo modificar
[ ] He leído SOURCE_OF_TRUTH.md · sé qué existe y qué no
[ ] He leído los Tier 2 relevantes a mi scope de hoy
[ ] He declarado intención al owner
[ ] He recibido confirmación para proceder
[ ] Memory MCP está activo (verificado con claude mcp list)
```

Cuando los 8 estén ✅: procede con confianza.

🐢💎 No velocity, only precision. El índice no es burocracia — es navegación.

---

```
INDICE_PROYECTO.md
Versión 1.0 · 17 mayo 2026
Aplica a: cualquier sesión de Claude Code en D:\Omega Master redes\
Compatible con: TODOS los documentos del proyecto
Próxima revisión: al cerrar Fase 1 (verificar que la estructura matchea la realidad post-deploy)
```
