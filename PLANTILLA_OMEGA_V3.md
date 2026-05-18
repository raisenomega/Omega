# PLANTILLA OMEGA V3 — Maestra del Proyecto
## Adaptación de PLANTILLA_UNIVERSAL_V3.md a OmegaRaisen
### Versión 1.0 · 17 mayo 2026

> **Propósito:** este documento es la versión OmegaRaisen-específica
> de la plantilla universal V3. Se diferencia de la universal en que
> incluye:
> 1. Las excepciones DDD I1 documentadas (Nano Banana + Veo 3.1)
> 2. La estructura concreta de bounded contexts de OmegaRaisen
> 3. Los routings específicos de los 37 agentes IA + 45 organizacionales
> 4. Las reglas P1-P5 con la formulación particular del SaaS multi-tenant
> 5. Los riesgos y guardrails específicos del negocio
>
> Si se usara este doc como base para otro proyecto Raisen Agency,
> sustituir las secciones marcadas [OMEGA-SPECIFIC] por las del nuevo proyecto.

---

# PARTE 1 — IDENTIDAD DEL PROYECTO

## [OMEGA-SPECIFIC] Datos canónicos

```
NOMBRE                OmegaRaisen ("Master Redes")
PROBLEMA QUE RESUELVE Operación de marketing digital para PYMEs y agencias
                      con 37 agentes IA bajo NOVA, supervisados por SENTINEL
USUARIO PRIMARIO      (1) Reseller agency (white-label)
                      (2) Cliente final del reseller (PYME, profesional)
                      (3) Owner OMEGA (raisenomega)
DATO MÁS VALIOSO      Brand Voice Corpus × Performance × Decisiones evaluadas
                      (los 3 datasets descritos en PRD §5 P2)
REGLA INMUTABLE       confidence ≥ 7 + brand_voice_check + compliance_check
                      + dentro de LIMITS_OMEGA hardcoded
MÉTRICA DE ÉXITO      SENTINEL ≥ 95 sostenido · 100% clients health=verde
                      costo ≤ $5/mes/cliente · cero secrets en commits
ESTADO                Reset arquitectónico mayo 2026 — V3 compliance build
```

## Las 4 preguntas fundacionales

Ya respondidas en `PRD_RECONSTRUIDO.md` Sección 5. Resumen aquí:

```
P1 — Plataforma SaaS multi-tenant white-label · operación 37+ agentes IA
P2 — Brand Voice Corpus + Performance × Contexto + agent_memory evaluado
P3 — Cero acción comercial/reputacional sin confidence ≥ 7 + checks
P4 — SENTINEL ≥ 95 + health verde + costo controlado + cero leaks
```

---

# PARTE 2 — ARQUITECTURA

## Stack confirmado (= SOURCE_OF_TRUTH.md §7)

## Las 4 capas — aplicadas a OmegaRaisen

```
PRESENTATION
  Frontend:    src/pages/* (rutas) · src/components/* (UI)
  Backend:     backend/app/api/routes/* (38 routers FastAPI)

APPLICATION
  Frontend:    src/bc-{N}/application/* (use cases por contexto)
  Backend:     backend/app/services/* + use cases en cada bc

DOMAIN  (cero imports externos)
  Frontend:    src/bc-{N}/domain/* (tipos, validators, business rules)
  Backend:     backend/app/domain/* + backend/app/bc_cognition/domain/*

INFRASTRUCTURE
  Frontend:    src/integrations/* (Supabase client, API client)
  Backend:     backend/app/infrastructure/* (adapters, repos)
               backend/app/bc_cognition/infrastructure/* (Claude, Nano, Veo)
```

## Bounded Contexts de OmegaRaisen

```
src/
├── bc-01-clients/           Gestión de clientes finales (PYMEs)
├── bc-02-content-lab/       Generación de contenido (texto, imagen, video)
├── bc-03-calendar/          Calendario editorial y scheduling
├── bc-04-analytics/         Métricas y reportes
├── bc-05-resellers/         White-label tenancy
├── bc-06-sentinel/          Security & health monitoring
├── bc-07-oracle/            Intelligence briefs estratégicos
└── bc-cognition/            ⭐ AI orchestration · siempre presente

backend/app/
├── api/routes/              Presentation (38 routers)
├── agents/                  22 agent implementations (a refactor a bc_cognition)
├── services/                Cross-cutting services
├── workers/                 8 cron jobs (SENTINEL, ORACLE, news, etc.)
├── domain/                  Domain types y validators
├── infrastructure/          Adapters
└── bc_cognition/            ⭐ AI cognition layer
    ├── domain/
    │   ├── persona_nova.py
    │   ├── limits_omega.py
    │   ├── conviction.py
    │   ├── routing_table.py
    │   └── episodic_memory.py
    ├── application/
    │   ├── use_agent.py
    │   ├── context_builder.py
    │   └── memory_query.py
    └── infrastructure/
        ├── anthropic_adapter.py    ÚNICO entry Claude
        ├── nano_banana_adapter.py  ÚNICO entry Gemini Image
        ├── veo3_adapter.py         ÚNICO entry Veo Video
        ├── memory_repository.py
        └── langfuse_observer.py
```

---

# PARTE 3 — REGLAS DE CERO TOLERANCIA

Ver `DDD_REGLAS_OMEGA.md` para detalle completo de las 60+ reglas.

Resumen ejecutivo por categoría:

```
A  — DDD y Arquitectura          A1-A10 (4 capas, bounded contexts, etc.)
C  — Código TS/Python            C1-C10 (no any, strict, archivos ≤100L)
I  — IA y Cognition              I1-I10 ★ con excepciones Nano Banana + Veo 3.1
G  — Guardrails y Seguridad      G1-G10 (SHA1, secretos, RLS, etc.)
M  — Memoria y Corpus            M1-M5  (agent_memory + pgvector)
B  — Construcción Claude Code    B1-B5  (CLAUDE.md, hooks, agents)
T  — Testing y Evals             T1-T5  (tests + promptfoo + smoke)
E  — Auto-evolución              E1-E5  (P1-P5 inmutables, bias detect)
O  — Operación y Deploy          O1-O5  (vault, logs, rollback)
X  — Omega-específico            X1-X5  (SENTINEL, NOVA, crons, Stripe)
```

## Las 5 reglas que se citan más en code review

```
A2 — Domain puro (sin imports externos)
C1 — Cero `any` en TS / `Any` en Python
I1 — Solo Anthropic + 2 excepciones documentadas
G1 — SHA1 de limits_omega.py verificable
C4 — Archivos ≤100L (excepciones documentadas)
```

---

# PARTE 4 — CONSTRUCCIÓN CON CLAUDE CODE

## Setup del .claude/

```
.claude/
├── settings.json                       Registra hooks + agents + skills + behavior
├── hooks/
│   ├── protect-guardrails.py           PreToolUse: bloquea modif a archivos protegidos
│   ├── check-file-length.py            PostToolUse: warn >75L, error >100L
│   └── verify-on-stop.sh               Stop: verifica estado pre-cierre
├── agents/
│   ├── auditor.md                      Opus read-only: análisis arquitectónico
│   ├── memory-writer.md                Haiku: persiste decisiones en agent_memory
│   └── context-checker.md              Haiku: verifica bootstrap de sesión
└── skills/
    ├── iniciar-fase/SKILL.md           Procedimiento al empezar fase
    ├── cerrar-ciclo/SKILL.md           Procedimiento al cerrar fase
    ├── auditoria/SKILL.md              Lanzar auditoría sobre scope
    └── registrar-deuda/SKILL.md        Documentar deuda nueva en SOURCE_OF_TRUTH
```

## MCPs recomendados para OmegaRaisen

```bash
claude mcp add supabase --env SUPABASE_URL=$SUPABASE_URL ...
claude mcp add github --env GITHUB_TOKEN=$GITHUB_PAT
claude mcp add context7
claude mcp add memory
```

## Plan Mode

Activar para cambios que tocan ≥3 archivos. Configurado en `.claude/settings.json`:
```json
{
  "behavior": {
    "planModeThreshold": 3
  }
}
```

---

# PARTE 5 — OPERACIÓN

## Routing de modelos Anthropic

```
HAIKU    claude-haiku-4-5-20251001    clasificación, lookup, texto corto
         Agentes: hashtag_gen, emoji_suggestor, sentiment_analyzer,
                  caption_optimizer, bio_generator, client_context_builder,
                  brand_voice_checker, url_extractor, pdf_extractor

SONNET   claude-sonnet-4-6             default — razonamiento + creatividad
         Agentes: content_creator, strategy, brand_voice, analytics,
                  scheduling, copywriter, trend_hunter,
                  competitive_intelligence, monitor, engagement,
                  seo_optimizer, image_prompt_writer, video_prompt_writer,
                  community_moderator, influencer_scout, compliance_checker,
                  quality_control, news_monitor, competitor_tracker

OPUS     claude-opus-4-7               decisiones críticas, reputacionales
         Agentes: orchestrator, crisis_manager, oracle_service, nova_chat,
                  ab_testing_analysis, report_generator, audit_reviewer,
                  growth_hacker, sentinel_security
```

## Routing de modelos Google (excepciones)

```
NANO BANANA — IMAGEN
  default:  gemini-3.1-flash-image-preview      (Nano Banana 2)
  premium:  gemini-3-pro-image-preview          (texto-en-imagen)
  legacy:   gemini-2.5-flash-image              (bulk simple)

VEO 3.1 — VIDEO
  default:  veo-3.1-generate-preview
  cheap:    veo-3.1-lite-generate-preview       (alto volumen)
```

## Persona NOVA — CEO Agent

```python
NOVA_PERSONA = """
Soy NOVA, el CEO virtual de OmegaRaisen.

Mi rol: orquestar 37 agentes especializados para operar la presencia
digital de tus clientes mientras tú escalas tu agencia.

Principios que NO violo:
1. La marca de tu cliente es el activo. Cero acción sin certeza.
2. confidence < 7 → te consulto en vez de actuar
3. Crisis pública → propongo draft, NUNCA respondo solo
4. Costo del cliente > $5/día → degrado routing, te notifico
5. Cada decisión queda registrada con outcome evaluable

Hablo en {idioma_owner}. Soy conciso, directo, basado en datos.
NUNCA exagero capacidades ni invento métricas.
"""
```

(Implementación completa en `bc_cognition/domain/persona_nova.py`)

## Memoria

```
agent_memory                Decisiones de cada agente con confidence + outcome
agent_log                   Llamadas a Claude/Nano/Veo (granular, observabilidad)
training_pairs              Dataset curado para fine-tuning futuro (M5)
```

Cada decisión significativa → INSERT en agent_memory.
A 24-72h → UPDATE was_correct según outcome real.

---

# PARTE 6 — VERIFICACIÓN

## Pre-commit (developer local)

```bash
git diff --check                                  # whitespace clean
```

## Pre-push (validate-before-push.sh — 9 checks)

```
1. C1+C2   Cero any / @ts-ignore / type: ignore
2. I1      Solo Anthropic + excepciones autorizadas
3. A2      Domain puro
4. G6      Cero secretos hardcoded
5. G9      Cero mock/fake/dummy en producción
6. G2      SHA1 limits_omega.py intacto
7. C4      Archivos ≤100L
8. T4      TypeScript compila
9. T5      Tests pasando
```

## Pre-deploy (CI · X1-X5 omega-específicos)

```
X1   SENTINEL score ≥ 95
X2   SHA1 personas intacto
X3   8/8 crons activos post-deploy
X4   Stripe webhooks idempotentes (test E2E)
X5   Brand voice check passing en pipeline
```

---

# PARTE 7 — DOCUMENTOS COMPLEMENTARIOS

```
SOURCE_OF_TRUTH.md                   ⭐ leer al inicio de cada sesión
PRD_RECONSTRUIDO.md                  Visión del producto reconstruida
CLAUDE.md                            Constitución ≤60L
DDD_REGLAS_OMEGA.md                  Contrato técnico (60+ reglas)
PROTOCOLO_SEGURIDAD_OMEGA.md         Defensa en profundidad
PROTOCOLO_IDENTIDAD_GIT_OMEGA.md     includeIf para identidad por repo
MIGRATION_PLAN_OMEGA.md              5 fases con timeline día-por-día
README.md                            Onboarding para nuevos contribuyentes
```

---

# PARTE 8 — APROBACIÓN

```
[ ] Esta plantilla refleja la arquitectura objetivo de OmegaRaisen
[ ] Las excepciones I1 (Nano Banana + Veo 3.1) están documentadas correctamente
[ ] El routing Haiku/Sonnet/Opus está acordado
[ ] Los bounded contexts propuestos representan los dominios reales del negocio
[ ] Procedo con MIGRATION_PLAN_OMEGA.md Fase 1

Firmado:  _______________________  Ibrain Raisen (CEO)
Fecha:    _______________________
```

---

```
PLANTILLA_OMEGA_V3.md
Versión 1.0 · 17 mayo 2026
Compatible con: PLANTILLA_UNIVERSAL_V3.md (base) + adaptaciones [OMEGA-SPECIFIC]
Próxima revisión: post Phase 1 (verificar adherencia real al plan)
```
