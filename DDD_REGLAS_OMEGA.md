# DDD + REGLAS DE CERO TOLERANCIA — OMEGARAISEN
## Contrato Inviolable del Proyecto OmegaRaisen
### Versión 1.0 · 17 mayo 2026 · Adaptado de DDD_REGLAS_CERO_TOLERANCIA universal

> **Propósito:** Este documento define las reglas que NUNCA se violan en
> OmegaRaisen, sin excepción. Es el contrato técnico del proyecto.
>
> **Diferencia con la versión universal:** este documento incluye las
> excepciones explícitamente documentadas y aprobadas por el owner,
> y las traduce al lenguaje Python+TypeScript del stack OmegaRaisen.
>
> **Cómo usar:**
> 1. Este archivo vive en la raíz del repo `raisenomega/Omega`
> 2. Pre-push hook verifica TODAS las reglas
> 3. Cualquier violación → push bloqueado, sin negociación
>
> **El principio madre:**
> Reglas claras + enforcement determinístico = sistema robusto.
> Reglas claras + cumplimiento voluntario = sistema frágil.

---

# LAS 5 LEYES FILOSÓFICAS INMUTABLES (OMEGA)

```
P1 — VERDAD BRUTAL
   OmegaRaisen reporta a sus resellers y clientes la realidad sin
   adornar. Si un post no se publicó, se reporta así. Si una métrica
   es estimada, se marca como estimada. Cero "datos sintéticos"
   en dashboards de cliente (DEBT-002 — Math.random() en analytics).

P2 — OBJETIVO PRIMARIO
   Preservar la reputación del cliente final. Cualquier acción que
   pueda dañar la marca del cliente (post incorrecto, respuesta
   automática a queja, contenido fuera de tono) requiere aprobación
   humana. La marca del cliente es el activo. No es negociable.

P3 — CONVICCIÓN MÍNIMA
   Sin ≥ 2 señales independientes confirmadas Y confidence ≥ 7:
   action = "hold_for_human_review". Ningún componente puede hacer
   override de esta regla. Aplicable a Content Creator, Strategy,
   Crisis Manager, Publisher.

P4 — ANTI-IMPULSIVIDAD
   Ningún agente posteará "porque está trending ahora" sin cruce
   con brand_voice del cliente. Crisis manager NUNCA responde
   crisis públicas automáticamente — solo alerta y propone draft.

P5 — APRENDIZAJE HONESTO
   Cada decisión de cada agente → INSERT en agent_memory con
   was_correct=null. A 24-72h: UPDATE was_correct según outcome.
   Errores se registran con detalle, no se minimizan.
```

---

# ÍNDICE DE REGLAS

```
CATEGORÍA A — DDD Y ARQUITECTURA           (A1-A10)
CATEGORÍA C — CÓDIGO Y TYPESCRIPT/PYTHON    (C1-C10)
CATEGORÍA I — IA Y COGNITION                (I1-I10) ★ con excepciones documentadas
CATEGORÍA G — GUARDRAILS Y SEGURIDAD        (G1-G10)
CATEGORÍA M — MEMORIA Y CORPUS              (M1-M5)
CATEGORÍA B — CONSTRUCCIÓN (CLAUDE CODE)    (B1-B5)
CATEGORÍA T — TESTING Y EVALS               (T1-T5)
CATEGORÍA E — AUTO-EVOLUCIÓN                (E1-E5)
CATEGORÍA O — OPERACIÓN Y DEPLOY            (O1-O5)
CATEGORÍA O — OMEGA-ESPECÍFICO              (X1-X5) ★ nuevo en este doc
```

---

# CATEGORÍA A — DDD Y ARQUITECTURA

## A1 · Las 4 Capas Son Obligatorias

```
ENFORCE       Estructura verificada por scripts/verify-architecture.sh
ESTRUCTURA    Backend:  app/{presentation, application, domain, infrastructure}/
              Frontend: src/bc-{N}-{nombre}/{domain, application, infrastructure}/
                        + src/bc-cognition/{domain, application, infrastructure}/
SEVERIDAD     CRÍTICA — refactor obligatorio antes de cualquier feature nueva
EXCEPCIÓN     FASE 2 del MIGRATION_PLAN permite estructura plana legacy
              temporalmente. FASE 3 obliga a esta regla.
```

## A2 · Cero Imports Externos en Domain

```
ENFORCE       grep -rE "from (anthropic|google|openai|supabase|fastapi|react)"
              backend/app/*/domain/  src/bc-*/domain/
SEVERIDAD     CRÍTICA — push bloqueado
EXCEPCIÓN     Ninguna
```

## A3 · Bounded Contexts Explícitos

```
ENFORCE       Estructura de carpetas + naming convention
EJEMPLO OMEGA src/bc-01-clients/
              src/bc-02-content-lab/
              src/bc-03-calendar/
              src/bc-04-analytics/
              src/bc-05-resellers/
              src/bc-06-sentinel/
              src/bc-07-oracle/
              src/bc-cognition/      ← SIEMPRE PRESENTE
```

## A4 · bc-cognition de Primera Clase

```
ESTRUCTURA OBLIGATORIA
   backend/app/bc_cognition/
   ├── domain/
   │   ├── persona_nova.py            # System prompt CEO Agent
   │   ├── limits_omega.py            # Guardrails Object.freeze equivalente
   │   ├── conviction.py              # Reglas P3 confidence ≥ 7
   │   └── episodic_memory.py         # Tipos de memoria
   ├── application/
   │   ├── use_agent.py               # Caso de uso principal
   │   └── context_builder.py         # Ensamblaje contexto ≤2k tokens
   └── infrastructure/
       ├── anthropic_adapter.py       # ÚNICO punto de llamada a Claude
       ├── nano_banana_adapter.py     # ÚNICO punto de llamada Gemini Image
       ├── veo3_adapter.py            # ÚNICO punto de llamada Veo Video
       └── memory_repository.py       # Persistencia agent_memory
```

## A5 · Result<T, Error> / Result tuple en Python

```
PYTHON CANON  from typing import Tuple
              Result = Tuple[bool, T | None, Error | None]
              def ok(value): return (True, value, None)
              def err(error): return (False, None, error)
TS CANON      type Result<T, E> = { ok: true; value: T } | { ok: false; error: E }
              ok = <T>(v: T): Ok<T> => ({ ok: true, value: v })
              err = <E>(e: E): Err<E> => ({ ok: false, error: e })
SEVERIDAD     MEDIA — convención requerida en dominio y aplicación
```

## A6-A10 — Aplican estándar V3

`Readonly<>` en TS · Value Objects (Money, Email, BrandSlug) · Mappers solo
en infrastructure (snake_case DB ↔ camelCase domain) · flujo unidireccional ·
naming `{Contexto}.{capa}.{tipo}` (TS) / `{tipo}_{nombre}.py` (Python).

---

# CATEGORÍA C — CÓDIGO Y TYPESCRIPT/PYTHON

## C1 · Cero `any` (TS) / Cero `Any` (Python)

```
ENFORCE TS    grep -rE "(:\s*any\b|as any\b|@ts-ignore)" src/ --include="*.ts*"
ENFORCE PY    grep -rE "(:\s*Any|cast\(Any|# type: ignore)" backend/app/ --include="*.py"
SEVERIDAD     CRÍTICA — push bloqueado
EXCEPCIÓN     Tests con justificación inline
```

## C2-C3 — strict mode

```
TS: tsconfig.json "strict": true + 9 flags activos
PY: mypy --strict en CI (por integrar)
```

## C4 · Archivos ≤75 Líneas

```
ENFORCE         Hook PostToolUse de Claude Code + script pre-push
WARN            >75 líneas
BLOCK           >100 líneas
EXCEPCIÓN ÚNICA Archivos autogenerados o de configuración con rationales:
                 · src/integrations/supabase/types.ts                    (autogen)
                 · src/components/ui/* (shadcn)                          (autogen)
                 · openapi_*.json                                        (autogen)
                 · backend/app/bc_cognition/domain/limits_omega.py       (constantes
                   inmutables + rationales documentados + self-checks · split
                   degradaría la atomicidad del SHA1 baseline · regla G2)
SCRIPT          scripts/validate-before-push.sh enforces
DEUDA EXISTENTE 202 archivos backend >75L (DEBT-004) — refactor por fases
```

## C5-C10 — Aplican estándar V3

Una responsabilidad por archivo · sin mutación directa · `Object.freeze()` en
constantes compartidas · imports absolutos con aliases · funciones puras en
domain · tipos externos mapeados a tipos de dominio.

---

# CATEGORÍA I — IA Y COGNITION  ★ CON EXCEPCIONES DOCUMENTADAS

## I1 · Solo Anthropic para Texto/Razonamiento — CON 2 EXCEPCIONES

```
REGLA BASE    Cero referencias a openai, groq, deepseek, mistral, runwayml,
              fal-client en el codebase para texto/razonamiento.

EXCEPCIONES DOCUMENTADAS Y APROBADAS POR OWNER (17 may 2026):

EXCEPCIÓN 1 — Google Nano Banana para GENERACIÓN DE IMÁGENES
  · Proveedor:   Google (google-genai SDK)
  · Justificación: Calidad superior actual + character consistency
                   para brand assets recurrentes
  · Modelos permitidos:
      · gemini-3.1-flash-image-preview  (Nano Banana 2, default)
      · gemini-3-pro-image-preview      (Pro, premium)
      · gemini-2.5-flash-image           (legacy bulk)
  · Aislado en:  backend/app/bc_cognition/infrastructure/nano_banana_adapter.py
  · Re-evaluación: Q4 2026 si Anthropic lanza generación de imágenes
                   competitiva (vía claude.ai o API)

EXCEPCIÓN 2 — Google Veo 3.1 para GENERACIÓN DE VIDEO
  · Proveedor:   Google (google-genai SDK · misma key)
  · Justificación: Único modelo production-ready con audio nativo
                   sincronizado · alternativa a Runway/FAL
  · Modelos permitidos:
      · veo-3.1-generate-preview         (default)
      · veo-3.1-lite-generate-preview    (alto volumen)
  · Aislado en:  backend/app/bc_cognition/infrastructure/veo3_adapter.py
  · Re-evaluación: Q4 2026 si Anthropic lanza generación de video

EXCEPCIÓN 3 — Voyage AI para EMBEDDINGS (memoria semántica ARIA · DEBT-048)
  · Proveedor:   Voyage AI (voyageai SDK)
  · Justificación: Anthropic no ofrece API de embeddings · la memoria
                   attention-based de ARIA (pgvector + similitud) necesita
                   un encoder. Solo vectores · NUNCA texto/razonamiento.
  · Modelos permitidos:
      · voyage-3-large  (output_dimension=1024, default)
  · Aislado en:  backend/app/bc_cognition/infrastructure/voyage_adapter.py
  · Aprobado por owner: 27 may 2026
  · Re-evaluación: Q4 2026 si Anthropic lanza embeddings propios

ENFORCE       Pre-push hook bloquea cualquier import de:
                openai, groq, deepseek, mistral, runwayml, fal_client, fal-client
              Permite google-genai SOLO si está bajo paths:
                backend/app/bc_cognition/infrastructure/nano_banana_adapter.py
                backend/app/bc_cognition/infrastructure/veo3_adapter.py
              Permite voyageai SOLO bajo:
                backend/app/bc_cognition/infrastructure/voyage_adapter.py
SCRIPT
   #!/bin/bash
   if grep -rE "from (openai|groq|deepseek|mistralai|runwayml|fal_client)" \
        backend/app/ src/ --include="*.py" --include="*.ts*" 2>/dev/null \
        | grep -v ".test."; then
     echo "❌ I1 violado: proveedor IA prohibido detectado"
     exit 1
   fi
   if grep -rE "from google\.genai|from google_genai|google-genai" \
        backend/app/ --include="*.py" 2>/dev/null \
        | grep -v "bc_cognition/infrastructure/(nano_banana|veo3)_adapter\.py"; then
     echo "❌ I1 violado: google-genai usado fuera de adapters autorizados"
     exit 1
   fi
SEVERIDAD     CRÍTICA — push bloqueado
```

## I2 · Routing por Tarea (Haiku/Sonnet/Opus)

```
TABLA OBLIGATORIA OMEGA:

  AGENTE                       MODELO              JUSTIFICACIÓN
  ──────────────────────────   ─────────────       ────────────────────
  hashtag_generator            Haiku 4.5           Clasificación rápida
  emoji_suggestor              Haiku 4.5           Lookup contextual
  caption_optimizer            Haiku 4.5           Iteración corta
  sentiment_analyzer           Haiku 4.5           Clasificación
  bio_generator                Haiku 4.5           Texto corto
  aria_1                       Haiku 4.5           Conversacional básico (Adopción)

  content_creator              Sonnet 4.6          Generación creativa default
  strategy                     Sonnet 4.6          Planificación táctica
  brand_voice                  Sonnet 4.6          Análisis de tono
  analytics                    Sonnet 4.6          Síntesis de insights
  scheduling                   Sonnet 4.6          Decisiones de timing
  copywriter                   Sonnet 4.6          Copy persuasivo
  trend_hunter                 Sonnet 4.6          Detección + síntesis
  competitive_intelligence     Sonnet 4.6          Análisis competitivo
  monitor                      Sonnet 4.6          Salud + alertas
  aria_2                       Sonnet 4.6          Conversacional estándar (Básico)
  aria_3                       Sonnet 4.6          Conversacional avanzado (Pro)
  aria_4                       Sonnet 4.6          near-NOVA context (Pro+addons)

  orchestrator                 Opus 4.7            Coordinación multi-agente
  crisis_manager               Opus 4.7            Decisión crítica reputacional
  oracle_service               Opus 4.7            Brief estratégico semanal
  nova_chat (CEO)              Opus 4.7            Conversación ejecutiva
  ab_testing_analysis          Opus 4.7            Análisis multi-variable
  report_generator             Opus 4.7            Reportes auditables

PROHIBIDO     Usar Opus para hashtag generation "porque es mejor".
              Costo 6x sin beneficio medible.
```

## I3-I10 — Aplican estándar V3

`cache_control: ephemeral` obligatorio en system prompts · persona concreta
(NOVA, ATLAS, LUNA por agente) · P1-P5 en system prompt · contexto ≤2,000
tokens · primacy+recency · JSON estructurado para datos numéricos ·
confidence < 7 → HOLD código · SDK Anthropic solo en `bc_cognition/infra/`.

---

# CATEGORÍA G — GUARDRAILS Y SEGURIDAD

## G1 · Archivo de Guardrails Inmutable

```
ARCHIVO        backend/app/bc_cognition/domain/limits_omega.py
CONTENIDO      LIMITS_OMEGA (frozen dict equivalente Python)
               MIN_CONFIDENCE_TO_ACT = 7
               MAX_POSTS_AUTO_PER_DIA_CLIENTE = 3
               MAX_USD_AUTO_AD_SPEND = 50
               MAX_USD_DIARIO_API_POR_CLIENTE = 5
               MAX_TOKENS_CONTEXT_DINAMICO = 2000
               MIN_HORAS_ENTRE_POSTS = 2
               ACCIONES_PROHIBIDAS = frozenset([...])
```

## G2 · SHA1 Verificable

```
BASELINE       scripts/guardrails-sha1.txt
SCRIPT         scripts/verify-guardrails.sh
ENFORCE        Pre-push hook + CI/CD
```

## G3-G10 — Aplican estándar V3

Cambio requiere test que falla primero · acciones prohibidas hardcoded · RLS
en todas las tablas con user_id/client_id/reseller_id/org_id · cero secretos
hardcoded · validación de entrada con Result · pre-push 11 checks · cero
mock/fake/dummy en producción · permisos mínimos por subagente.

---

# CATEGORÍA M — MEMORIA Y CORPUS

## M1 · `agent_memory` Existe Desde Día 1

```
SCHEMA OBLIGATORIO    Ver supabase/migrations/00002_agent_memory_pgvector.sql

CREATE TABLE agent_memory (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       uuid REFERENCES auth.users(id),
  client_id     uuid REFERENCES clients(id),
  reseller_id   uuid REFERENCES resellers(id),
  agent_code    text NOT NULL,
  memory_type   text NOT NULL CHECK (memory_type IN ('episodic','semantic','procedural')),
  context       text,
  decision      text,
  reasoning     text,
  outcome       text,
  was_correct   boolean,
  confidence    integer CHECK (confidence BETWEEN 0 AND 10),
  embedding     vector(1536),
  created_at    timestamptz DEFAULT now(),
  evaluated_at  timestamptz
);
```

## M2-M5 — Aplican estándar V3

pgvector activo + índice ivfflat · RLS en agent_memory · cada decisión con
was_correct eventual · `training_pairs` preparada desde día 1.

---

# CATEGORÍA B — CONSTRUCCIÓN (CLAUDE CODE)

## B1-B5 — Aplican estándar V3

CLAUDE.md ≤60L · Hooks determinísticos en `.claude/hooks/` · Subagentes
especializados · MCPs antes del primer feature (Supabase, GitHub, Context7,
Memory) · Plan Mode para cambios ≥3 archivos.

---

# CATEGORÍA T — TESTING Y EVALS

## T1-T5 — Aplican estándar V3

Tests en limits + Value Objects + Mappers + classify/decide logic ·
Promptfoo evals para bc_cognition · Smoke test pre-deploy · Pre-push hook
11/11 verde · Tests pasando pre-commit.

---

# CATEGORÍA E — AUTO-EVOLUCIÓN

## E1-E5 — Aplican estándar V3

P1-P5 inmutables peso=1.0 · Constitution Evolution solo con ≥100 episodios
cerrados · Bias detection semanal · Prompt evolution con A/B test ·
Fine-tuning solo con ≥50K training_pairs.

---

# CATEGORÍA O — OPERACIÓN Y DEPLOY

## O1-O5 — Aplican estándar V3

Vault secrets verificados pre-deploy · Logs estructurados en `agent_log` ·
Rollback probado · Crons verificados post-deploy · Observabilidad LLM
(Langfuse).

---

# CATEGORÍA X — OMEGA-ESPECÍFICO

## X1 · SENTINEL Score ≥ 95 Pre-Deploy

```
REGLA         Antes de cada deploy a producción: SENTINEL full_scan
              debe retornar security_score ≥ 95/100 y deploy_decision="APPROVE"
ENFORCE       scripts/check-sentinel-score.sh
SCRIPT
   #!/bin/bash
   SCORE=$(curl -s $RAILWAY_URL/api/v1/sentinel/scan/full | jq .security_score)
   if [ "$SCORE" -lt 95 ]; then
     echo "❌ X1 violado: SENTINEL score $SCORE < 95 — deploy bloqueado"
     exit 1
   fi
```

## X2 · Persona NOVA Inmutable en System Prompt

```
REGLA         El system prompt de NOVA (CEO Agent) vive en
              bc_cognition/domain/persona_nova.py con SHA1 propio
ENFORCE       scripts/verify-personas.sh
RAZÓN         La identidad del CEO virtual no muta sin aprobación owner
```

## X3 · 16 Cron Workers Verificados Post-Deploy

```
FUENTE        backend/app/main.py (scheduler.start() en @app.on_event startup, ~L163).
              ⚠️ backend/app/workers/scheduler.py NO es el scheduler activo (código
              legacy, 3 jobs, start_scheduler() sin caller · DEBT-SCHEDULER-LEGACY-DUP).
REGLA         Después de cada deploy: verificar que los 16 cron jobs
              están activos en APScheduler
JOBS          vault_scan (cron 2 AM) · db_guardian (cron 5 AM) · sentinel_brief (cron 7 AM) ·
              pulse_monitor (interval 5 min) · oracle_weekly_brief (cron lun 7 AM) ·
              aria_learning_report (cron lun 7:05 · DEBT-101) ·
              news_monitor (interval 2h) · competitor_tracker (interval 6h) ·
              trend_spotter (interval 12h) · brand_dna_refresh (cron 3 AM · DEBT-044) ·
              video_jobs_orphan_cleanup (interval 1h · DEBT-045) ·
              outcome_evaluator (cron 4 AM · 4A-2 PASO 3 ciclo auto-aprendizaje) ·
              credit_period_reset (cron 0:05 fin-de-mes · DEBT-052) ·
              decision_evaluator (cron :30 cada hora · DEBT-100 ARIA_LEARNING_LOOP) ·
              strategy_generator (cron 7:10 diario · DEBT-096 F2 · filtra por cadencia/cliente) ·
              hermes_ping (interval 5 min · DEBT-HERMES-CORE f1 · salud integraciones → mcp_health_log)
ENFORCE       Endpoint /api/v1/system/cron-status debe retornar 16/16 active
```

## X4 · Stripe Connect Webhooks Idempotentes

```
REGLA         Cada handler de webhook de Stripe verifica
              webhook_events.event_id no procesado antes (idempotencia)
ENFORCE       Test E2E con duplicado intencional
RAZÓN         Stripe reintenta webhooks — sin idempotencia: doble facturación
```

## X5 · Brand Voice Check Antes de Cada Post Generado

```
REGLA         Ningún post pasa de draft a scheduled sin brand_voice_check
              que retorne match_score ≥ 0.7
ENFORCE       Test del pipeline content_lab
RAZÓN         Es la regla P2 traducida a código: la marca del cliente
              es el activo. Cero post fuera de tono.
```

---

# SCRIPT DE VERIFICACIÓN ÚNICA

Ver `scripts/validate-before-push.sh` para implementación completa con 11 checks
(numerados 0/11 a 10/11 · `TOTAL=11` en el script):

```
0.  Identidad git (bloqueante · raisenomega / raisenagencypr@gmail.com)
1.  C1+C2: Cero any / @ts-ignore (TS) y cero Any / type: ignore (Python)
2.  I1:    Solo Anthropic (con excepciones Nano Banana + Veo 3.1 en adapters)
3.  A2:    Domain puro (sin imports externos)
4.  G6:    Sin secretos hardcoded
5.  G9:    Sin mock/fake/dummy en producción
6.  G2:    SHA1 de limits_omega.py intacto
7.  C4:    Archivos ≤100 líneas (error) / ≤75 líneas (warning)
8.  T4:    TypeScript compila sin errores
9.  T5:    Tests pasando (Vitest + pytest)
10. X2:    SHA1 personas (NOVA/ARIA) intacto
```

**NO están en el gate pre-push ejecutable** (el doc los listaba antes, pero el script
no los corre): `X1` (SENTINEL score ≥95 — es verificación pre-deploy, no pre-push) y
`X4` (idempotencia Stripe webhooks — cubierto por test suite T5, no como check propio).
Siguen siendo reglas del proyecto; simplemente no son checks del gate diario.

---

# TABLA DE CONSECUENCIAS

```
CRÍTICA (push bloqueado):       C1, C2, I1, G2, G6, A2, T4, T5, X4
ALTA (warning + correctivo):    C4 (>75L), C8, I6, X1, X3
MEDIA (code review):            A6, A7, C9, X5
BAJA (recomendación):           C5, B5
```

---

# ANTI-PATRONES PROHIBIDOS — OMEGA-ESPECÍFICOS

```
AP-OMEGA-001  "Voy a usar OpenAI temporal mientras refactorizo"
              Realidad: el refactor es Phase 3. Hasta entonces, las funciones
              que dependían de OpenAI se desactivan o se mueven a Anthropic.
              Cero excepciones temporales que se quedan.

AP-OMEGA-002  "El reseller necesita esto YA, lo subo sin SENTINEL pasing"
              Realidad: X1 dice score ≥ 95. SENTINEL en rojo = deploy bloqueado.
              Si el reseller necesita YA, se le explica que la integridad del
              sistema sostiene a todos sus clientes.

AP-OMEGA-003  "NOVA puede responder esa crisis pública porque es obvia"
              Realidad: P4 + X5. Crisis manager NUNCA responde solo.
              Genera draft, alerta owner, espera firma.

AP-OMEGA-004  "Voy a editar limits_omega.py en hot-fix"
              Realidad: G3. Cambio en guardrails requiere test que falla
              primero + rotación de SHA1 + commit del nuevo baseline.

AP-OMEGA-005  "El frontend puede consultar Supabase directo, es más rápido"
              Realidad: viola A1 (4 capas). El frontend habla con FastAPI
              (excepto auth de Supabase y storage URLs públicos).
              DEBT-008 documentada · refactor en Phase 3.
```

---

# CHECKLIST PRE-PROYECTO (OMEGA bootstrap)

```
═══════════════════════════════════════════════════════════════
DOCUMENTOS FUNDACIONALES                                       
═══════════════════════════════════════════════════════════════
[X] SOURCE_OF_TRUTH.md
[X] PRD_RECONSTRUIDO.md
[X] CLAUDE.md (≤60 líneas)
[X] DDD_REGLAS_OMEGA.md (este archivo)
[X] PROTOCOLO_SEGURIDAD_OMEGA.md
[X] PROTOCOLO_IDENTIDAD_GIT_OMEGA.md
[X] MIGRATION_PLAN_OMEGA.md
[X] PLANTILLA_OMEGA_V3.md
[X] README.md

═══════════════════════════════════════════════════════════════
INFRAESTRUCTURA DE ENFORCEMENT                                 
═══════════════════════════════════════════════════════════════
[X] scripts/validate-before-push.sh
[X] scripts/verify-guardrails.sh
[X] scripts/bootstrap.sh
[ ] .husky/pre-push  (configurar en bootstrap)
[ ] tsconfig.json con strict: true + 9 flags

═══════════════════════════════════════════════════════════════
CLAUDE CODE STACK                                              
═══════════════════════════════════════════════════════════════
[X] .claude/settings.json
[X] .claude/hooks/protect-guardrails.py
[X] .claude/hooks/check-file-length.py
[X] .claude/hooks/verify-on-stop.sh
[X] .claude/agents/auditor.md
[X] .claude/agents/memory-writer.md
[X] .claude/agents/context-checker.md
[X] .claude/skills/iniciar-fase/SKILL.md
[X] .claude/skills/cerrar-ciclo/SKILL.md
[X] .claude/skills/auditoria/SKILL.md
[X] .claude/skills/registrar-deuda/SKILL.md

═══════════════════════════════════════════════════════════════
ARQUITECTURA INICIAL                                           
═══════════════════════════════════════════════════════════════
[X] backend/app/bc_cognition/{domain,application,infrastructure}/
[X] backend/app/bc_cognition/domain/limits_omega.py
[X] SHA1 registrado en scripts/guardrails-sha1.txt
[ ] System prompt NOVA con persona concreta + P1-P5
[ ] Routing Haiku/Sonnet/Opus configurado
[ ] cache_control: ephemeral activo

═══════════════════════════════════════════════════════════════
DATABASE INICIAL                                               
═══════════════════════════════════════════════════════════════
[X] Migración 00001_initial_consolidated.sql
[X] Migración 00002_agent_memory_pgvector.sql
[X] Migración 00003_rls_complete.sql
[ ] Aplicadas en Supabase nuevo (rwlnihoqhxwpbehibgxu)

═══════════════════════════════════════════════════════════════
PRIMER COMMIT                                                  
═══════════════════════════════════════════════════════════════
[ ] git config user.email = raisenagencypr@gmail.com
[ ] git add <archivo> por archivo (NUNCA `git add .`) && git status muestra TODO esperado
[ ] bash scripts/validate-before-push.sh pasa 11/11
[ ] git commit -m "feat: bootstrap V3 stack (OmegaRaisen rebuild)"
[ ] git push -u origin main exitoso
```

---

# NOTA FINAL

> **Este documento es contrato, no sugerencia.**
>
> Si una regla aquí se viola, no es una "decisión técnica diferente".
> Es una violación del contrato. Las consecuencias son automatizadas
> (push bloqueado, tests fallando, hooks gritando). No dependen del
> juicio humano. Esa es la diferencia entre un sistema robusto y uno
> que se desmorona bajo presión.
>
> **Cuándo modificar este documento:**
> Solo cuando hayas operado OmegaRaisen ≥6 meses y hayas identificado
> UNA regla que demonstrablemente no aporta valor, con evidencia de
> agent_memory.
>
> **Cuándo NO modificar:**
> Por presión del reseller. Por urgencia de un cliente. Por "esta vez
> es diferente". Las reglas existen específicamente para esos momentos.

```
DDD_REGLAS_OMEGA.md
Versión 1.0 · 17 mayo 2026
Compatible con: PLANTILLA_OMEGA_V3.md + SOURCE_OF_TRUTH.md
Próxima revisión: Q4 2026 (re-evaluar excepciones I1)
Estado: documento vivo — actualizar con evidencia, nunca con prisa
```
