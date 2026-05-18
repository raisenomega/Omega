# OMEGARAISEN — PRD RECONSTRUIDO

## Versión 1.0 · 17 mayo 2026
### Reconstruido por Claude leyendo el repositorio existente

---

## SECCIÓN 1 — IDENTIDAD DEL PROYECTO

```
NOMBRE                OmegaRaisen ("Master Redes")
DESCRIPCIÓN           Plataforma SaaS multi-tenant white-label que opera la presencia
                      digital de PYMEs y agencias mediante 37+ agentes IA organizados
                      bajo NOVA (CEO) y supervisados por SENTINEL (security).
USUARIOS OBJETIVO     (1) Agencias de marketing que revenden la plataforma con su marca
                          (resellers white-label)
                      (2) Clientes finales de cada agencia (PYMEs, profesionales)
                      (3) Operación interna OMEGA (owner = raisenomega)
ESTADO ACTUAL         [X] Producción · operación de resellers + clientes activos
                      → Reset arquitectónico en curso (mayo 2026)
FECHA INICIO REPO     df61048 · "Initial commit: OmegaRaisen project setup"
ÚLTIMO COMMIT         1e2ed99 · Wed Apr 8 2026 · "feat: replace Tavily with Brave Search"
TOTAL COMMITS         302
LÍNEAS DE CÓDIGO      Python (backend): 35,569 L  ·  360 files
                      TS/TSX (frontend): 8,867 L  ·   94 files
                      SQL migrations:    25 files ·  ~2,800 L
OWNER PRINCIPAL       Jorge Ibrain  (commits firmados [deprecado] — debe pasar a raisenomega)
REPO ANTERIOR         repo backend anterior (deprecado) (backend)
                      repo frontend anterior (deprecado, Lovable) (frontend Lovable)
REPO NUEVO            github.com/raisenomega/Omega  (monorepo unificado)
```

---

## SECCIÓN 2 — STACK TÉCNICO

```
FRONTEND
  Framework:    React 18.3 · TypeScript 5.8
  Build:        Vite 5.4 + plugin SWC
  UI library:   shadcn/ui (Radix) + Tailwind CSS 3.4
  Estado:       React Query 5.83 (server) + React Context (auth, theme)
  Forms:        React Hook Form 7.61 + Zod 3.25
  Routing:      React Router DOM 6.30 · 12 rutas en App.tsx:31

BACKEND
  Lenguaje:     Python 3.11
  Runtime:      uvicorn (ASGI)
  Framework:    FastAPI 0.109 · Pydantic 2.10 + pydantic-settings 2.6
  ORM:          SQLAlchemy 2.0 + raw Supabase SDK (Python 2.7)
  Auth:         bcrypt (passlib 1.7) + python-jose JWT
  Schedulers:   APScheduler 3.10 (8 cron jobs, ver SOURCE_OF_TRUTH §1)
  Scrapers:     BeautifulSoup 4.12 + pypdf 4.0

DATABASE
  Tipo:         PostgreSQL 15
  Provider:     Supabase (nuevo: rwlnihoqhxwpbehibgxu.supabase.co)
  Extensiones:  pgvector (por habilitar) · uuid-ossp · pgcrypto
  Storage:      Supabase Storage bucket `reseller-media` + futuro `client-assets`

DEPLOY
  Frontend:     Vercel (un solo proyecto, sin Lovable)
  Backend:      Railway (nixpacks → uvicorn)
  Database:     Supabase Cloud

AI PROVIDERS (POST-DECISIÓN 17 may 2026)
  Texto/razon:  ANTHROPIC ÚNICAMENTE
                · anthropic 0.34+
                · Modelos: claude-haiku-4-5-20251001 · claude-sonnet-4-6 · claude-opus-4-7
  Imágenes:    GOOGLE NANO BANANA (excepción documentada)
                · google-genai SDK
                · Modelos: gemini-3.1-flash-image-preview (default)
                          gemini-3-pro-image-preview     (premium para texto-en-imagen)
                          gemini-2.5-flash-image          (legacy bulk)
  Video:       GOOGLE VEO 3.1 (excepción documentada)
                · google-genai SDK
                · Modelos: veo-3.1-generate-preview (default)
                          veo-3.1-lite-generate-preview (alto volumen)
  ELIMINADOS:   openai · groq · deepseek · runwayml · fal-client · dall-e-3

APIs EXTERNAS
  · Brave Search (web research) — desde commit 1e2ed99
  · Stripe (Connect onboarding + subscriptions + webhooks)
  · Resend / SendGrid (email transaccional — por confirmar)
  · Meta Developer (Instagram/FB Graph API — DEBT-003, pendiente)
  · TikTok Business API (DEBT-003)

MONITOREO
  Observabilidad LLM:  Langfuse (por integrar)
  Health/Pulse:        SENTINEL interno cada 5 min
  Errores:             FastAPI global exception handler (main.py:175)
```

---

## SECCIÓN 3 — LO QUE EL SISTEMA HACE

### FUNCIONALIDAD CORE

1. **Generación de contenido multi-formato** — texto, imagen, video por cliente, alineado a brand voice
2. **Calendario editorial inteligente** — Strategy Agent + Scheduling Agent posicionan posts en horarios óptimos
3. **Distribución multi-plataforma** — Publisher (Instagram, Facebook, Twitter, LinkedIn, TikTok, YouTube)
4. **Analytics consolidados** — Analytics Agent procesa engagement + Sentiment Analyzer
5. **Inteligencia competitiva** — Competitive Intelligence Agent + Trend Hunter Agent
6. **Gestión de crisis** — Crisis Manager Agent + alertas SENTINEL en tiempo real
7. **Multi-tenant white-label** — cada reseller con branding propio (logo, colores, dominio)
8. **Sub-brands por cliente** — un cliente puede operar varias marcas separadas
9. **Upsell workflow** — cliente solicita agente extra → admin aprueba → Stripe cobra recurrente
10. **NOVA chat asistente** — interfaz conversacional con el CEO Agent

### FLUJOS PRINCIPALES

```
FLUJO 1: GENERACIÓN Y APROBACIÓN DE POST
  Trigger:     Usuario abre Content Lab y pide post
  Entry point: api/routes/content_lab/router.py + handlers/generate_text.py
  Pipeline:    Client Context Agent → Brand Voice Agent → Content Creator (Anthropic)
              → Quality Control → Compliance Check → guardar como `draft`
  Output:      Post draft en content_lab_generated con confidence + reasoning

FLUJO 2: PUBLICACIÓN AUTOMÁTICA EN HORARIO
  Trigger:     APScheduler cada minuto → Publisher Agent revisa cola
  Entry point: workers/scheduler.py (por crear) · scheduled_posts table
  Pipeline:    Publisher → confirmar oauth tokens → llamar API plataforma
              → registrar resultado en agent_memory + agent_log
  Output:      Post publicado · engagement empezará a registrarse

FLUJO 3: ALERTA DE CRISIS
  Trigger:     SENTINEL pulse_monitor cada 5 min (main.py:75)
              o Crisis Manager detecta sentiment_score < threshold
  Entry point: workers/news_monitor_worker.py · services/sentinel_service.py
  Pipeline:    Detección → CrisisManagerAgent NUNCA responde solo
              → Genera draft + notifica owner por NOVA chat + email
  Output:      Alert + draft response listo para revisión humana

FLUJO 4: ONBOARDING DE RESELLER
  Trigger:     Owner crea reseller desde admin panel
  Entry point: api/routes/resellers/admin.py
  Pipeline:    INSERT resellers + reseller_branding default
              → Stripe Connect onboarding link
              → Reseller configura branding (logo, colores, tagline)
              → /reseller/dashboard activo con health monitoring
  Output:      Reseller live con su white-label

FLUJO 5: ORACLE INTELLIGENCE BRIEF SEMANAL
  Trigger:     Cron lunes 7 AM AST (main.py:77)
  Entry point: services/oracle_service.py:generate_intelligence_brief
  Pipeline:    Cruza datos de 7 días · genera markdown summary
              → Llama Claude Opus para sintesis ejecutiva
              → INSERT oracle_briefs · notifica vía NOVA
  Output:      Brief estratégico semanal para el owner
```

---

## SECCIÓN 4 — LO QUE EL SISTEMA NO HACE

### NO INCLUYE

- **Generación de leads desde redes** (cold outreach automation) — fuera de scope inicial
- **Edición de video frame-a-frame** — Veo genera, no edita stitched
- **A/B testing on-platform real** — solo simulado con tráfico interno hasta tener oauth keys
- **CRM completo** — solo lleva clients básico, no es alternativa a HubSpot/Salesforce
- **E-commerce / checkout en redes** — no integra Shopify, no maneja carritos

### OUT OF SCOPE EXPLÍCITO

- **No publica en TikTok/Instagram hoy** — falta Meta Developer App approval (DEBT-003)
- **No factura a usuarios finales** — solo a resellers · usuarios finales pagan al reseller
- **No genera audio/voiceover** — Veo 3.1 ya incluye audio nativo, no se usa TTS separado
- **No tiene chat público para visitantes** — NOVA es solo para owner/reseller/cliente autenticado
- **No reemplaza al estratega humano** — propone, humano aprueba decisiones de marca

---

## SECCIÓN 5 — LAS 4 PREGUNTAS FUNDACIONALES (V3)

### P1 — ¿QUÉ PROBLEMA RESUELVE?

```
Centraliza la operación de marketing digital de PYMEs y agencias white-label:
generación, calendario, distribución, analytics e inteligencia competitiva.
Sustituye un equipo humano de 8-12 personas (community manager, copywriter,
diseñador, estratega, analista) por 37 agentes IA bajo NOVA (CEO virtual),
permitiendo a una agencia operar 50+ cuentas de cliente con 1-2 humanos
supervisores en lugar de 10-15.
```

### P2 — ¿CUÁL ES EL DATO MÁS VALIOSO A ACUMULAR?

```
Tres datasets en paralelo:

(a) Brand Voice Corpus por cliente
    Cada post aprobado por el cliente → fragmento de voz canónica.
    A 6 meses por cliente: ~500 ejemplos. A 24 meses: 2,000+.
    Valor: imposible de comprar, cero opciones de salida del cliente sin
    perder este corpus.

(b) Performance × Contexto
    Cada post publicado registra:
    metric_engagement × timestamp × tema × tono × season × competitor_state
    A 12 meses: dataset comprimido para entrenar router táctico propio
    sin necesidad de Claude.

(c) Decisiones del agente con outcome (agent_memory)
    Cada decisión IA → was_correct=true/false a 72h.
    Dataset de entrenamiento para fine-tuning Año 2-3.
    Target: 50,000 pares de calidad → modelo propio viable.
```

### P3 — ¿CUÁL ES LA REGLA QUE NUNCA SE PUEDE VIOLAR?

```
Ningún agente realiza una acción con impacto comercial o reputacional
sin: (a) confidence ≥ 7, (b) brand_voice check pasado,
     (c) compliance check pasado, (d) ESTAR DENTRO de los límites
hardcoded en bc_cognition/domain/limits_omega.py.

Concretamente: cero post automático >$50 ad spend, cero respuesta pública
a crisis sin draft humano, cero contacto a lead sin opt-in registrado,
cero modificación de Stripe subscription amount sin firma del cliente.

Equivalente al riskLimits.ts del playbook de trading: el guardrail último.
Modificarlo requiere commit de test que falla primero, y rotación del SHA1.
```

### P4 — ¿CÓMO SABES QUE ESTÁ FUNCIONANDO BIEN?

```
Cuatro métricas medidas continuamente:

(1) SENTINEL global score ≥ 95/100 sostenido 7 días
    (composite: tests verdes, deploy decisions APPROVE, cero secrets leaks)

(2) Reseller dashboard.health = "verde" para 100% de clientes activos
    (rojo si: post failures >5/día, sentiment <0.3, API costs >$15/día/cliente)

(3) ORACLE weekly brief calidad: review humana mensual,
    rating del brief ≥ 4/5 por owner

(4) Costo medio Anthropic API por cliente/mes ≤ $5 (P95 ≤ $15)
    Si excede: routing degrada de Sonnet→Haiku automáticamente
```

---

## SECCIÓN 6 — DIAGNÓSTICO V3 (cumplimiento actual)

### ARQUITECTURA

- [⚠️] 4 capas (presentation/application/domain/infrastructure): **parcial** — backend tiene domain/application/infrastructure pero presentation está en `api/routes/`. Frontend no aplica DDD.
- [❌] Bounded Contexts identificables: **NO** — backend agrupa por tipo (routes, agents, services), no por dominio.
- [❌] bc-cognition existe: **NO** — está pendiente crear `backend/app/bc_cognition/`.
- [❌] Archivo de guardrails con Object.freeze() (limits_omega.py): **NO existe**.
- [❌] SHA1 verificable: **NO** — sin baseline registrado.

### CONSTRUCCIÓN (Claude Code)

- [❌] CLAUDE.md: **no existe** (en este repo)
- [❌] Hooks en `.claude/hooks/`: **NO**
- [❌] Subagentes en `.claude/agents/`: **NO**
- [❌] Skills en `.claude/skills/`: **NO**
- [❌] MCPs configurados: **sin evidencia**
- [❌] Graphify integrado: **NO**
- [❌] Plan Mode usado: **convención no establecida**
- [❌] Promptfoo evals: **NO**
- [⚠️] Langfuse/Helicone: **langsmith>=0.1.0** en requirements pero sin código que lo use

### OPERACIÓN

- [⚠️] System prompt con persona concreta: **parcial** — NOVA tiene persona descrita en docs/01_OMEGA_AGENTS_CORE_PROMPTS.md, pero no enforced en código
- [❌] `cache_control: ephemeral` activo: **no verificado en código** del provider
- [⚠️] `agent_memory` existe: **NO** como tabla — existe `omega_activity` con schema distinto
- [❌] pgvector activo: **NO** — usa Qdrant externo
- [⚠️] Routing Haiku/Sonnet/Opus: **parcial** — existe `services/llm_router.py:73` pero no enforced

### AUTO-EVOLUCIÓN

- [❌] Constitution Evolution: **NO**
- [❌] Prompt Evolution: **NO** (existe Prompt Vault pero es manual)
- [❌] Bias Detection: **NO**
- [❌] Pattern Library: **NO**
- [❌] `training_pairs` preparada: **NO**

---

## SECCIÓN 7 — PLAN DE ADOPCIÓN V3

Ver `MIGRATION_PLAN_OMEGA.md` para detalle completo. Resumen aquí:

### FASE 0 — Documentación fundacional (entrega: hoy)
- SOURCE_OF_TRUTH.md · PRD_RECONSTRUIDO.md · CLAUDE.md · README.md
- DDD_REGLAS_OMEGA.md · PROTOCOLO_SEGURIDAD_OMEGA.md · PROTOCOLO_IDENTIDAD_GIT_OMEGA.md
- MIGRATION_PLAN_OMEGA.md · PLANTILLA_OMEGA_V3.md

### FASE 1 — Infraestructura nueva (2-3 días)
- Crear repo `raisenomega/Omega` con monorepo (frontend + backend)
- Crear proyecto Vercel
- Crear proyecto Railway
- Configurar Supabase nuevo `rwlnihoqhxwpbehibgxu.supabase.co`
- Setup identidad git includeIf
- Rotar todas las API keys

### FASE 2 — Lift & shift "tal cual está" + cambios de proveedor (5-7 días)
- Migrar código backend al repo nuevo
- Migrar código frontend (último estado de r-omegaagency) al repo nuevo
- Aplicar 25 migraciones consolidadas + nuevas (agent_memory + RLS gaps)
- Swap imagen: DALL-E 3 → Nano Banana
- Swap video: Runway/FAL → Veo 3.1
- Mantener OpenAI/Groq/DeepSeek TEMPORALMENTE para no romper funciones
- Deploy → verificar 100% paridad funcional

### FASE 3 — Refactor a DDD progresivo (4-6 semanas)
- Crear `bc_cognition/` + mover claude_service ahí
- Crear limits_omega.py + scripts SHA1
- Reemplazar OpenAI text calls por Anthropic (cumple I1)
- Split de archivos >75L por R-LINES-001

### FASE 4 — Claude Code stack + auto-evolución (1-2 semanas)
- .claude/hooks + agents + skills + settings
- Promptfoo baseline para 5 agentes core
- Langfuse en anthropic_adapter
- Constitution Evolution + bias detection

---

## SECCIÓN 8 — RIESGOS Y DEUDA DETECTADA

**CRÍTICOS:**
```
1. 5 proveedores IA en código vs 1 declarado (Anthropic only) — viola I1
2. Frontend habla directo a Supabase sin pasar por FastAPI — arquitectura
3. 202 archivos backend >75L · 13 archivos >300L
4. Cero tests reales · sin pre-push enforcement
5. 8 migraciones sin RLS en tablas con identificadores de propietario
```

**ADVERTENCIAS:**
```
6. 3 directorios de migraciones distintos (supabase/, backend/supabase_migrations/, backend/migrations/)
7. Modelo Claude declarado vs implementado inconsistente (3 strings distintos en código)
8. node_modules/ commiteado en el zip (343 MB de los cuales 330 son node_modules)
9. test_*.py y test_*.json sueltos en raíz (8 archivos)
10. Sentinel_files/ y omega_persistence/ contienen `persistence_router.py` duplicado
```

**MEJORAS RECOMENDADAS:**
```
11. Consolidar 95 archivos .md de docs en estructura clara docs/{guides,protocols,reports}/
12. Crear .github/workflows/ con CI mínimo (typecheck + tests + validate-before-push)
13. Activar Dependabot para Anthropic SDK + google-genai
14. Configurar Renovate para Python deps con security advisories
15. Cron de db_guardian incluir reporting de tablas sin RLS detectadas
```

---

## SECCIÓN 9 — APROBACIÓN DEL OWNER

```
[ ] PRD reconstruido refleja la realidad del proyecto
[ ] Las 4 preguntas fundacionales son correctas
[ ] El plan de adopción V3 es realista
[ ] Procedo a generar bc_cognition + hooks + agents + skills (Fase 3)

Firmado:  _________________________  Ibrain Raisen (CEO)
Fecha:    _________________________
```

---

```
PRD_RECONSTRUIDO.md · OmegaRaisen · v1.0 · 17 mayo 2026
Compatible con: PLANTILLA_OMEGA_V3.md + DDD_REGLAS_OMEGA.md
Próximo paso: aprobar Fase 1 (infraestructura nueva)
```
