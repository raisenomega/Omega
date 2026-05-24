# OMEGARAISEN — FUENTE ÚNICA DE VERDAD

> Documento fundacional. Se lee al inicio de cada sesión.
> Versión 1.0 · 17 mayo 2026 · Compatible con PLANTILLA_OMEGA_V3.md

```
PROYECTO       OmegaRaisen (Master Redes)
OWNER          Jorge Ibrain · Raisen Agency
DOMINIO        Operación r-omega.agency
REPO ÚNICO     github.com/raisenomega/Omega
INFRA NUEVA    Supabase: rwlnihoqhxwpbehibgxu.supabase.co
               Railway:  por crear (replaces omegaraisen-production-2031)
               Vercel:   por crear (un solo proyecto frontend, sin Lovable)
ESTADO         Reset arquitectónico desde repos viejos
               (repo backend anterior (deprecado) + repo frontend anterior (deprecado))
PROVEEDOR IA   Anthropic (ÚNICO para texto/razonamiento)
EXCEPCIONES    Google Nano Banana (imágenes) · Google Veo 3.1 (video)
```

---

## SECCIÓN 1 — LO QUE EXISTE (verificado en código)

| Componente | Estado | Evidencia |
|------------|--------|-----------|
| Backend FastAPI | ✅ | `backend/app/main.py:43` · 38 routers registrados |
| 22 agentes IA implementados | ✅ | `backend/app/agents/*.py` (22 archivos `.py`) |
| 45 agentes organizacionales seedeados | ✅ | `migrations/create_omega_agents.sql:14` (NOVA, ATLAS, LUNA…) |
| Schema multi-tenant | ✅ | `supabase_migrations/002_resellers_multitenant.sql:9` |
| Auth con bcrypt + JWT | ✅ | `api/routes/auth/jwt_utils.py` |
| Stripe Connect billing | ✅ | `api/routes/billing/webhook.py:1` |
| 8 cron workers autónomos | ✅ | `main.py:72-85` SENTINEL/ORACLE/News/Competitor/Trend |
| SENTINEL security system | ✅ | `services/sentinel_service.py:1` + 4 mixins |
| ORACLE intelligence brief | ✅ | `services/oracle_service.py:1` (lunes 7 AM) |
| NOVA chat agent (CEO) | ✅ | `api/routes/nova/handlers/chat.py` |
| Content Lab (texto + imagen + video) | ✅ | `api/routes/content_lab/handlers/*.py` |
| Reseller dashboard backend | ✅ | `api/routes/reseller/router.py` (commit fa0b5a8) |
| Sub-brands CRUD | ✅ | `api/routes/sub_brands/router.py` (commit 8049b67) |
| Upsell workflow | ✅ | `api/routes/upsell/router.py` (commit fa0b5a8) |
| Feature usage tracking | ✅ | `api/routes/clients/feature_usage_router.py` |
| Frontend Vite + React + shadcn/ui | ✅ | `package.json:1` + `src/App.tsx:31` con 12 rutas |
| Brave Search integration | ✅ | `infrastructure/tools/web_search_tool.py` (commit 1e2ed99) |
| Mem0 + Qdrant vector store | ⚠️ | importado pero no es pgvector nativo |
| RLS en tablas iniciales | ✅ | `supabase/migrations/20260212230856...sql:60-65` |

## SECCIÓN 2 — LO QUE NO EXISTE (aunque se diga)

| Afirmación | Realidad |
|------------|----------|
| "Sistema con Solo-Anthropic" | NO. Hay 5 proveedores IA activos: Anthropic, OpenAI, Google Gemini, Groq, DeepSeek |
| "37/37 agents 100% funcionales" | Parcial. 22 archivos `agents/*.py`, varios sin tests, varios con OpenAI hardcoded |
| "Tests pasando" | NO. 1 solo test: `src/test/example.test.ts`. Cero pytest en backend |
| "Frontend → Backend FastAPI" | NO. El frontend del zip (src/) habla DIRECTO a Supabase, no llama a `/api/v1/*` |
| "DDD aplicado" | Parcial. Existe `domain/`, `application/`, `infrastructure/` en backend pero mezclado. NO existe `bc-cognition/` |
| "Archivos ≤200L" | NO. 202 archivos backend >75L. 13 archivos >300L (`trend_hunter_agent.py:316`) |
| "RLS en todas las tablas" | NO. Migrations 002-008 NO activan RLS. `resellers`, `reseller_branding`, `clients` (modif), `leads` sin RLS |
| "Pipeline CI/CD verificable" | NO. Sin `.github/workflows/`, sin `validate-before-push.sh`, sin hooks |
| "agent_memory + pgvector" | NO. Usa Qdrant externo. Sin tabla `agent_memory` con `vector(1536)` |
| "training_pairs preparada" | NO. Tabla no existe |
| "Modelo Claude 4.6" (declarado) | INCONSISTENTE. `config.py:40` dice `claude-sonnet-4-20250514`. Provider dice `claude-sonnet-4-5-20250929` |
| "DALL-E 3, Runway, FAL en uso" | DEPRECADO por decisión del owner (17 may 2026). Reemplazo: Nano Banana + Veo 3.1 |

## SECCIÓN 3 — REGLAS INMUTABLES (P1-P5)

```
P1 — VERDAD BRUTAL
   OmegaRaisen reporta a sus resellers/clientes la realidad sin
   adornar. Si un post no se publicó, se reporta así. Si una métrica
   es estimada, se marca como estimada. Cero "datos sintéticos" en
   dashboards de cliente.

P2 — OBJETIVO PRIMARIO
   Preservar la reputación del cliente final. Cualquier acción que
   pueda dañar la marca del cliente (post incorrecto, respuesta
   automática a queja, contenido fuera de tono) requiere aprobación
   humana. La marca del cliente es el activo. No es negociable.

P3 — CONVICCIÓN MÍNIMA
   Ningún agente publica/responde/contacta sin: (a) confidence ≥ 7,
   (b) brand voice check pasado, (c) compliance check pasado.
   Si falta una de las tres, action="hold_for_human_review".

P4 — ANTI-IMPULSIVIDAD
   Ningún agente posteará "porque está trending ahora" sin cruce
   con brand_voice del cliente. Crisis manager NUNCA responde
   crisis públicas automáticamente — solo alerta y propone draft.

P5 — APRENDIZAJE HONESTO
   Cada decisión de cada agente → INSERT en agent_memory con
   was_correct=null. A 24-72h: UPDATE con outcome. Errores se
   registran con detalle, no se minimizan.
```

## SECCIÓN 4 — GUARDRAILS DEL NEGOCIO

> Viven en `backend/app/bc_cognition/domain/limits_omega.py` con SHA1 verificado.

```
MIN_CONFIDENCE_TO_ACT          = 7            # escala 0-10
MAX_POSTS_AUTO_PER_DIA_CLIENTE = 3            # más → human review
MAX_USD_AUTO_AD_SPEND          = 50           # más → owner approval
MAX_USD_DIARIO_API_POR_CLIENTE = 5            # circuit breaker AI costs
MAX_TOKENS_CONTEXT_DINAMICO    = 2000         # I6: Lost-in-the-Middle
MIN_HORAS_ENTRE_POSTS          = 2            # anti-spam
ACCIONES_PROHIBIDAS            = [
  "respond_to_complaint_publicly",            # crisis → solo draft
  "contact_lead_without_consent",             # CAN-SPAM/GDPR
  "delete_client_brand_file",                 # destructivo
  "modify_stripe_subscription_amount",        # contractual
  "auto_post_to_paid_account_no_oauth",       # impossible w/o key
]
```

## SECCIÓN 5 — MÉTRICA PRINCIPAL

```
SENTINEL global score ≥ 95/100 sostenido 7 días
  · Cero false positives en crisis_manager_agent durante un mes
  · 100% de los clientes activos con reseller_dashboard.health = verde
  · Costo medio Claude por cliente/mes ≤ $5 (P95 ≤ $15)
  · Cero secretos hardcoded detectados en pre-push hook
```

## SECCIÓN 6 — DEUDA TÉCNICA CONOCIDA

| ID | Item | Por qué existe | Tiempo | Impacto |
|----|------|----------------|--------|---------|
| DEBT-001 | `scheduled_post_repository.py` = 265L | Crecimiento orgánico | 2h | Bajo |
| DEBT-002 | Math.random() en analytics frontend | Datos sintéticos pre-integración | 4h | Alto (P1) |
| DEBT-003 | Instagram/TikTok/Facebook APIs sin keys | Falta Meta Developer App | 40h | Bloquea publicación |
| DEBT-004 | 202 archivos backend >75L (cifra estimada pre-lift&shift) | Falta enforcement | — | subsumido por DEBT-017 (post-lift&shift cifra real) |
| DEBT-005 | 5 proveedores IA cuando solo Anthropic permitido | Histórico | 40h | Crítico (DDD I1) |
| DEBT-006 | Sin `agent_memory` con pgvector | Usa Qdrant externo | 8h | Alto (M1, M2) |
| DEBT-007 | 3 directorios de migraciones distintos | Histórico Lovable+backend | 6h | Medio |
| DEBT-008 | Frontend habla directo a Supabase | Bootstrap Lovable | 80h | Bajo (funcional) |
| DEBT-009 | Sin promptfoo evals | No implementado | 16h | Medio |
| DEBT-010 | Sin observabilidad LLM (Langfuse) | langsmith en deps pero no usado | 8h | Medio |
| DEBT-011 | Sin tests reales (1 solo test) | Velocidad sobre solidez | 80h | Alto |
| DEBT-012 | mem0ai/qdrant-client/langsmith comentados en `backend/requirements.txt:46-52` | Bootstrap Fase 0 (17 may 2026): `mem0ai>=0.1.0` requiere `sqlalchemy>=2.0.31` vs pin 2.0.25 (alineado con prod Railway). Descomentar requiere migración a pgvector+Langfuse (ya cubierta por DEBT-006+010) | 0h (subsumida en DEBT-006+010) | Bajo |
| DEBT-013 | `tsconfig.json` en modo Lovable laxo (sin strict, sin 9 aliases `@bc-*/*` V3) | Lift & shift §2.2 (18 may 2026): código Lovable escrito sin strict — preservar V3 bloquearía build con cientos de errores de `any`/null/unused. Re-aplicar strict V3 + aliases progresivamente durante refactor por bounded context Fase 3 §3.2. Backup V3 en `D:/tmp-lovable-extract/_v3_backups/tsconfig.v3.json` | 16h (re-strict por BC) | Alto (C1+C2) |
| DEBT-014 | 11+ archivos frontend >100L (Clients.tsx 448L, Content.tsx 306L, SettingsPage.tsx 291L, ClientDetail.tsx 286L, ClientAIConfig.tsx 277L, etc.) | Lift & shift §2.2 (18 may 2026): código Lovable no diseñado con regla 75/100L. Exception list en `scripts/validate-before-push.sh` check 7/10 para `src/pages/`, `src/hooks/`, `src/components/clients/` como **grace period Fase 2**. Cerrar antes/durante Fase 3 §3.3 split progresivo | 40h | Alto (C4) |
| DEBT-015 | 15+ `as any` / `as any[]` en hooks y pages del Lovable (useOrganization.ts 7×, Calendar.tsx, ClientDetail.tsx, Clients.tsx, Content.tsx) | Escape hatch Lovable para tablas Supabase sin types generadas (`audit_logs`, `posts`). Exception list en check 1/10 para `src/pages/`, `src/hooks/`, `src/components/clients/` como **grace period Fase 2**. Cerrar regenerando types con `supabase gen types typescript` + reemplazando casts durante Fase 3 §3.2 refactor por BC | 20h | Alto (C1+C2) |
| DEBT-016 | **CERRADA en §2.6 (18 may 2026)**: I1 100% compliance · 0 imports prohibidos en backend. Quedan **6 ocurrencias `# type: ignore` / `: Any`** en `base_agent.py:86` (1) y `providers/anthropic_provider.py:94/etc` (5) — estos son C2 (no I1) y serán cerrados durante refactor Fase 3 §3.2 por bounded context. Exception list en check 1/10 para `agents/`, `infrastructure/ai/providers/`, `models/` se mantiene mientras esos 6 type:ignore vivan | Lift & shift §2.1 (18 may 2026) + hot-swaps §2.4/§2.5/§2.6 cerraron los 10 I1 violators originales (openai_service, runway_agent, fal_video_agent, groq_agent, openai_provider, groq_provider, deepseek_provider, gemini_provider, ai_providers, llm/router) | 2h restantes (C2 cleanup) | Bajo (C2) |
| DEBT-017 | 163 archivos backend Lovable >100L (cifra real post-lift&shift). Top: `trend_hunter_agent.py` 316L, `analytics_agent.py` 313L, `engagement_agent.py` 306L, `scheduling_agent.py` 301L, `crisis_manager_agent.py` 298L | Lift & shift §2.1 (18 may 2026): código Lovable no diseñado con regla 75/100L. Exception list en check 7/10 para `backend/app/{agents,api,services,sentinel,workers,models,domain,infrastructure}/` como **grace period Fase 2**. `bc_cognition/` NO exento. Subsume y reemplaza DEBT-004 (cifra estimada). Cerrar en Fase 3 §3.3 split progresivo por bounded context | 80h | Alto (C4) |
| DEBT-018 | **CERRADA (22 may 2026 · Sprint 2 P1)** via commit `e4d13ef`: migración 00016 creó bucket `generated-images` (10MB · MIME whitelist jpeg/png/webp · RLS public read · service_role write vía bypass) + nuevo `bc_cognition/infrastructure/_storage_uploader.py` (62L · `upload_image_bytes(image_bytes, mime_type, client_id=None) -> str` con StorageUploadError fail-loud) + `_image_compat.py` refactoreado (71→76L) decodea base64 → upload → retorna URLs públicas persistentes en vez de data URIs. Cero breaking changes en callers legacy (kwarg `client_id` opcional · fallback folder `shared/`). Bucket `generated-videos` (500MB · video/mp4) también incluido en 00016 para acelerar cierre futuro de DEBT-019. **Original (histórico)**: imágenes Nano Banana se devolvían como data URIs >1MB · no aptas para DB ni redes sociales | — | 0h (cerrada) | — |
| DEBT-019 | **CERRADA (22 may 2026 · Sprint 2)** via commit `f2e2bb9`: `_storage_uploader.py` refactoreado a private `_upload_bytes` core + 2 wrappers públicos (`upload_image_bytes` backwards-compat + `upload_video_bytes` nuevo · MIME tables y bucket constants separados · bucket `generated-videos` 500MB/mp4 ya creado en 00016 Sprint 2 P1). `_video_compat.py` extendido (69→85L) con `_download_veo_uri(uri)` async usando `httpx.AsyncClient` con header `x-goog-api-key: $GEMINI_API_KEY` (timeout 120s para videos 5-50MB) → `upload_video_bytes(bytes, "video/mp4", client_id)` → URL persistente Supabase Storage. `client_id` opcional con fallback folder `shared/` (cero breaking change para callers legacy `content_lab/handlers/generate_video.py`). Si download/upload falla → `status='failed'` antes de que TTL del temp URI mate el video. **DEBT-020 sigue abierta**: sync poll 300s puede timeout en Vercel (frontend) · job queue pendiente Sprint 3+. **Original (histórico)**: videos Veo 3.1 se devolvían como URIs temporales de Google · TTL minutos/horas · URLs muertas tras expiración | — | 0h (cerrada) | — |
| DEBT-020 | **CERRADA (22 may 2026 · Sprint 2)** via commit `4b989fd`: migración 00018 creó tabla `video_generation_jobs(id PK uuid, client_id FK clients, prompt, ratio, status enum pending/running/completed/failed, video_url, error, metadata jsonb, created_at, started_at, completed_at)` + RLS (service_role ALL · authenticated SELECT own client) + index (client_id, created_at DESC). Application: nuevo `bc_cognition/infrastructure/video_job_repository.py` (68L · insert_pending + update_running/completed/failed + fetch_job · pattern función libre sync con _sb singleton + _now_iso helper). `bc_cognition/application/use_video_job.py` (73L · `create_video_job` inserta row + `scheduler.add_job('date', run_date=datetime.now(), args=[job_id])` lazy import del scheduler global · `_run_video_job` background worker con **double try/except orphan-safe** (si update_failed también falla, log explícito "ORPHAN" para debug visible) · `get_video_job` read). Handler V3 nuevo `api/routes/content_lab_v3/handlers/generate_video.py` (54L · POST `/generate-video` returns `{job_id, status: pending}` en ~50ms + GET `/generate-video/{job_id}` returns status con 404 sin leak si no es del cliente). 3 nuevos modelos en `content_lab_models.py` (GenerateVideoRequest + VideoJobStart/StatusResponse). Beneficio: Veo 3.1 (30-90s) ya NO bloquea HTTP request · Vercel timeout 10-30s no aplica · frontend hace polling cada 5s al GET endpoint. **Original (histórico)**: poll síncrono 300s dentro del endpoint HTTP causaba timeouts y degradaba throughput | — | 0h (cerrada) | — |
| DEBT-021 | Endpoint `/generate-video-runway/` y handler `handle_generate_video_runway` mantienen el nombre "runway" aunque internals ahora usan Veo 3.1. Frontend Lovable llama `/generate-video-runway/` — renombrar rompería contrato API | Hot-swap §2.5 (18 may 2026): "lift & shift" preserva contrato externo. **Cerrar durante Fase 3 §3.2 refactor por bounded context**: renombrar endpoint a `/generate-video/` + handler a `handle_generate_video` + actualizar frontend Lovable coordinadamente | 2h | Bajo (cosmético) |
| DEBT-022 | **CERRADA en §2.6 (18 may 2026)**: extendido `_image_compat.generate_image_compat()` con `reference_images_b64: Optional[List[str]] = None`. `generate_image.py` simplificado a single-path Nano Banana (`_generate_with_nano_banana` para generate y edit). `import fal_client` eliminado. 0 referencias a FAL en backend | — | 0h (cerrada) | — |
| DEBT-023 | **CERRADA (18 may 2026)**: `claude_service.model` bumped a `claude-sonnet-4-6`. También actualizado el string del response en `services/llm/router.py:LLMResponse.model`. Long-term routing dinámico por agent_code sigue cubierto por DEBT-024 | — | 0h (cerrada) | — |
| DEBT-024 | 48 callers de `claude_service.generate_text()` (drop-in §2.6 desde openai_service) siguen usando el wrapper Lovable en `infrastructure/ai/claude_service.py`. V3 manda que `bc_cognition/infrastructure/anthropic_adapter.py` sea el ÚNICO entry point a Claude. Hay duplicación con duplicate caching/timeout logic ausente en claude_service | Migración Fase 3 §3.2: cada bounded context refactoriza sus agents para llamar `anthropic_adapter.generate(agent_code=..., system=..., messages=...)` retornando Result<T,E>. Crea `_text_compat.py` si conviene mantener signature legacy durante transición. Eventualmente eliminar `claude_service.py` | 12h | Medio (DDD ÚNICO entry) |
| DEBT-025 | `services/ai_providers.py` + `services/llm/router.py` + `infrastructure/ai/agent_dispatcher.py` + `agent_registry.py` siguen vivos tras §2.6 con refactor mínimo (solo Anthropic). Duplican funcionalidad de `bc_cognition.domain.routing_table` + `bc_cognition.infrastructure.anthropic_adapter` V3 | Refactor Fase 3 §3.2: unificar el routing layer con bc_cognition V3. Eliminar agent_dispatcher/agent_registry o convertirlos en thin wrappers sobre routing_table. Actualizar callers que importan `AIProviders` / `generate_content` del router | 8h | Medio (consolidación) |
| DEBT-026 | **CERRADA (18 may 2026)**: `backend/app/config.py` CORS parser. `NoDecode` (plan original) no existe en `pydantic_settings 2.6.1`; pivote a campo `backend_cors_origins: str` (no-complex → sin JSON decode upstream) + `@property cors_origins_list` que expone List[str]. Validators legacy `@validator` removidos | — | 0h (cerrada) | — |
| DEBT-027 | **CERRADA (18 may 2026)**: `backend/app/config.py` `extra='forbid'` default de pydantic_settings 2.6.1 bloqueaba `Settings()` con 14 vars huérfanas en `.env` (vite_*, database_url, gemini_*, stripe_publishable, brave, resend, email_from, allowed_hosts, escalation_*, etc.). Fix: `extra="ignore"` en `class Config`. Bonus: eliminados 3 fields OpenAI dead (openai_api_key/model/image_model post §2.6 hot-swap) | — | 0h (cerrada) | — |
| DEBT-028 | **CERRADA (18 may 2026)**: `pydantic_settings` carga `.env` solo dentro de `settings` — `os.environ` queda vacío para 35 sites legacy que leen `os.getenv()` directo. 2 raises a nivel de módulo (`jwt_token_utils.py:12`, `auth_utils.py:14`) bloqueaban uvicorn import. Fix: (a) `load_dotenv(Path(__file__).resolve().parents[2]/".env")` al top de `main.py` puebla `os.environ` para todos; (b) 2 raises migrados a `settings.jwt_secret_key` (fail-fast preservado vía `Field(...)`). Resto de 33 sites cubierto por DEBT-029 | — | 0h (cerrada) | — |
| DEBT-029 | 33 occurrences en 21 archivos backend leen `os.getenv(...)` directo en vez de `settings.xxx`: bc_cognition adapters (3), billing/stripe_* (5), sentinel_vault.py (3), calendar_repository.py (2), agentic_runner*.py (5), ai_providers.py (1), tools/web_search_tool.py (1), admin/patch_solicitud.py (1), resellers/get_reseller_billing.py (1), clients/get_client_billing.py (1), omega handlers (2), nova/chat.py (1), monitor_agent.py (1), infrastructure/ai/agent_dispatcher.py (1), bc_cognition/anthropic_adapter (1), veo3_adapter (1), nano_banana_adapter (1), billing/checkout.py (2), billing/webhook.py (1). Funcionan vía DEBT-028 `load_dotenv` shim pero violan DDD (config layer único) | Refactor Fase 3 §3.2: cada bounded context migra sus `os.getenv()` a `settings.xxx`. Añadir fields faltantes en `Settings`: `brave_api_key`, `gemini_api_key`, `stripe_api_key`, `stripe_success_url`, `stripe_cancel_url`, `railway_environment`, `render` (sentinel infra detection), `qdrant_host`/`qdrant_port` (ya existen). Eliminar `load_dotenv` shim al final | 6h | Medio (DDD layer purity) |
| DEBT-030 | `backend/app/api/routes/agents/handlers/__init__.py` declara 5 handlers pero solo `handle_execute_agent` existía en disco. 4 archivos faltantes desde migración Lovable→V3 (`list_agents.py`, `get_agent.py`, `get_executions.py`, `get_logs.py`). Bloqueaba import de `app.main` aun cuando `router.py` solo invoca `execute_agent` + `execute_agent_agentic` (los otros 4 referenciados en `__init__.py` no son usados por endpoints) | **Solución temporal aplicada (18 may 2026)**: 4 stubs creados que raise `HTTPException(501)` con detail `"... · DEBT-030 · Fase 3"`. Ningún endpoint los expone hoy, son satisfacción de import de `__init__.py`. **Fase 3 §3.2**: (a) implementar real desde supabase agents/agent_executions/agent_logs tables, O (b) si endpoints no se exponen nunca, limpiar `__init__.py` y borrar stubs | 8h | Bajo (cosmético / migración faltante) |
| DEBT-031 | **CIERRE PARCIAL (20 may 2026)**: `client_context` ya existe (migración 00011 · 43 cols + RLS). Aún pendiente: `agent_executions` no existe + cols incorrectas en `scheduled_posts` referenciadas por handler legacy. `backend/app/api/routes/analytics/handlers/get_dashboard.py:120-185` referencia tablas `agent_executions` y `client_context` que **no existen en schema V3** (confirmado vía MCP list_tables: solo `clients`, `social_accounts`, `content_lab_generated`, `scheduled_posts`, `anti_fraud_signals`). Además referencia cols `scheduled_posts.is_active` y `scheduled_posts.scheduled_date` (real son `status` y `scheduled_for`). Endpoint `/api/v1/analytics/dashboard/` retornaría error 500 si se invoca. **Frontend NO lo usa** — `useDashboardData` hace queries Supabase directas con RLS (Step 2 §2.6 confirmado 18 may 2026) | Cleanup Fase 3 §3.2: (a) reescribir handler contra schema V3 real usando `clients/social_accounts/content_lab_generated/scheduled_posts/anti_fraud_signals`, O (b) eliminar endpoint si nunca se va a invocar desde frontend (consolidar contract de dashboard en Supabase JS directo) | 4h | Bajo (endpoint dead pero no bloqueante) |
| DEBT-032 | **CERRADA TOTAL (19 may 2026)**: Parte 1 (Migración 00006) trigger `AFTER INSERT ON auth.users` que auto-crea `clients` + `client_plans` Adopción 7d con `SECURITY DEFINER` · guard reseller owners · backfill `cliente@omega.com`. Parte 2 (Migración 00007 + `bc_billing/` + `billing_v3/`) Stripe Checkout endpoint + webhook handler con idempotencia X4 (UNIQUE event_id en `webhook_events`) + 3 dispatchers (checkout.completed → upsert client_plans · subscription.updated → sync period_end · subscription.deleted → downgrade graceful Adopción 7d) | — | 0h (cerrada) | — |
| DEBT-033 | **CERRADA TOTAL (20 may 2026)**: las 5 pages Lovable legacy (Content/Calendar/SettingsPage/Clients/ClientDetail) reescritas contra schema V3 real. SettingsPage V3 con profile/plan/payment (commit 130cc48). Clients.tsx con wizard onboarding completo + edit pre-poblado (commits ecd35a7/ab90076/78504f5). Content.tsx V3 con content_v3 endpoints + save/unsave + brand_voice_corpus learning (commit eb61136). Calendar.tsx V3 con scheduled_posts + status transitions + behavioral_events (este commit). Frontend Lovable consulta **5 tablas inexistentes en schema V3**: `profiles`, `posts`, `organizations`, `user_roles`, `audit_logs`. 18+ errores console por session por queries auto-firing. Pages afectadas (19 may 2026): (a) **Full Próximamente aplicado**: `Content.tsx`, `Calendar.tsx`, `SettingsPage.tsx` (core 100% broken); (b) **Surgical stub aplicado**: `Clients.tsx` (profile query stub, CRUD mutations fallan solo si user click), `ClientDetail.tsx` (teamMembers + posts arrays vacíos · tabs Agente/Posts en estado vacío); (c) `useOrganization.ts` stubbed completo (5 queries → no-op). Plus componente reusable `src/components/ComingSoon.tsx` | Rewrite Fase 3 §3.x mapeando contra schema V3 real: (1) `profiles` → `auth.users.user_metadata` + posiblemente tabla `user_profiles` nueva; (2) `posts` → split entre `content_lab_generated` (drafts/aprobaciones) y `scheduled_posts` (programación/publicación); (3) `organizations` → eliminar o modelar como tabla `tenants` separada; (4) `user_roles` → derivar de `resellers.owner_user_id` y `clients.user_id` o tabla `org_members` nueva; (5) `audit_logs` → tabla nueva con cols (actor_id, action, entity, before/after jsonb). Después rebuild de las 5 pages contra el nuevo schema | 40h | Alto (5 pages + 1 hook · UX/UI mayor) |
| DEBT-034 | `src/hooks/useAnalyticsData.ts` contiene 4 mock generators (`generateGrowthData`, `generateEngagementData`, `generateHeatmapData`, `generateTopPosts`) que rellenan toda la página `/analytics`. Hardcoded follower base = 0 (V3 no tiene `social_accounts.followers_count`). El crash original (`totalFollowers.toLocaleString()` undefined post Step 2) fue arreglado defensivamente, pero la página sigue siendo 100% mock | Rewrite Fase 3 §3.x: (a) sync Meta API alimenta `social_accounts.followers_count` (nueva col) o tabla `social_metrics` por timestamp; (b) `analytics_events` table real con (post_id, type, value, ts); (c) rebuild de los 4 generators contra ese schema. Alternativa más simple: eliminar `/analytics` page completa hasta que haya backend de analytics real | 16h | Medio (P1 violation pre-existente · pero crash arreglado) |
| DEBT-035 | **CERRADA TEMPORAL (19 may 2026)**: Bell badge `<span>3</span>` hardcoded en `src/components/layout/AppHeader.tsx` eliminado (última P1 violation pendiente del frontend). Botón Bell queda decorativo sin badge ni click handler · aria-label "Notificaciones" para accesibilidad | Restaurar el badge cuando exista endpoint `/notifications` + hook `useNotifications` que devuelva `count` real. Patrón: `{count > 0 && <span>{count}</span>}` condicional dentro del Button. Estimado: 8h (tabla notifications + endpoint + hook + integración) | 8h | Bajo (cosmético hasta que haya tabla notifications) |
| DEBT-036 | **NUEVA (19 may 2026)**: Lovable billing legacy module · 21 archivos referenciando Stripe en backend (`backend/app/api/routes/billing/{checkout,webhook,subscription,stripe_config,models,__init__}.py`, `clients/billing.py`, `clients/handlers/get_client_billing.py`, `resellers/reseller_billing.py`, `resellers/handlers/get_reseller_billing.py`, `infrastructure/supabase_service.py`, `infrastructure/supabase_billing_mixin.py`, plus refs cosméticas en omega/, admin/, upsell/, sentinel_vault.py, models/reseller_models.py). Path `/api/v1/billing/*` desregistrado de main.py en favor de `billing_v3/` V3 limpio. Código legacy queda en disco como referencia histórica · zero endpoints expuestos · zero código nuevo lo invoca | Cleanup Fase 3 §3.x: (1) eliminar `backend/app/api/routes/billing/` completo (todos los 7 archivos), (2) eliminar `clients/billing.py` + handler, (3) eliminar `resellers/reseller_billing.py` + handler, (4) refactor `supabase_billing_mixin` o eliminarlo si funcionalidad fue migrada a `bc_billing/application/`, (5) limpiar refs cosméticas en omega/admin/upsell/sentinel_vault | 8h | Bajo (legacy inerte · no bloqueante) |
| DEBT-043 | **NUEVA (20 may 2026)**: Sin índice composite en `content_lab_generated(client_id, is_saved)` para el endpoint GET /api/v1/content/. Hoy el query `WHERE client_id IN (...) AND is_saved=?` hace sequential scan · bajo volumen (Lovable mock data + content_v3 recién desplegado) lo hace tolerable. Cuando crezca a >5k filas habrá latencia perceptible. | Migración futura: `CREATE INDEX idx_content_client_saved ON content_lab_generated (client_id, is_saved, created_at DESC)` + `CREATE INDEX idx_content_client_type ON content_lab_generated (client_id, content_type)` para filter por tipo. Indexar cuando volumen lo justifique (P95 query >100ms) | 1h | Bajo (perf cosmético hasta escala) |
| DEBT-042 | **NUEVA (20 may 2026)**: `clients.region` column es single TEXT pero el Wizard V3 captura `regions: list[str]` (multi-país). Solución temporal en `create_client_onboarding.py`: `region = ",".join(regions)`. `GET /clients/profile` retorna `region: "PR,USA"` como string · `SettingsPage > ProfileSection` actualmente muestra el string crudo en lugar de chips. | Fase 3 § 3.x · 2 opciones: (a) migración 00013 ALTER TABLE clients ADD COLUMN regions text[] + backfill desde region.split(",") + UPDATE handlers; o (b) keep TEXT y parsear "PR,USA".split(",") en ProfileSection con multi-select Combobox igual al wizard. Opción (b) más rápida; (a) más DDD-pura | 3h | Bajo (display cosmético · no bloquea funcionalidad) |
| DEBT-039 | **NUEVA (20 may 2026)**: PDF parser para wizard onboarding (sec 10 · samples). Hoy `POST /api/v1/clients/{id}/parse-brand-pdf` retorna 501. Spec: usuario sube PDF con brand guide / pitch deck / portfolio · backend extrae con pypdf + Claude Haiku → auto-popula `client_context` (niche/vertical/business_what/audience/tone). | Fase 3 §3.x · (1) `pip install pypdf` (ya en requirements); (2) handler real: stream upload → pypdf extract text → Haiku prompt structured extraction → upsert client_context con campos extraídos + source='pdf_parsed' tag; (3) UI: progress bar + diff preview antes de aplicar | 12h | Medio (UX onboarding bonus · wizard manual funciona sin esto) |
| DEBT-040 | **NUEVA (20 may 2026)**: OAuth flows por plataforma social pendientes. `social_accounts` ya tiene cols `oauth_status/platform_account_id/access_token_encrypted/token_expires_at/is_business_account/linked_facebook_page_id/connection_metadata` (migración 00011) pero todas vacías hoy. Wizard captura @handle + metadata pero `oauth_status='not_connected'` permanente hasta integrar. ARIA no puede auto-publicar sin tokens reales. | Fase 2 Meta MCP · (1) Meta Developer App + App Review (Instagram Business + Facebook Pages); (2) TikTok for Developers approval; (3) LinkedIn API access; (4) YouTube Data API key; (5) backend OAuth flow handler por plataforma + token refresh worker; (6) Stripe-style webhook para token expiry alerts. Cubre DEBT-003 también | 40h | Crítico (bloquea publicación · ARIA solo puede draft hasta entonces) |
| DEBT-041 | **CERRADA (20 may 2026)** via migración 00012: bucket `brand-files` creado · 10MB · whitelist MIME (png/jpeg/webp/svg/pdf) · 3 RLS policies en storage.objects (client_select + client_insert por foldername[1]==client_id + service_role full). Aplicado vía CLI y versionado idempotente. **Original (histórico)**: Supabase Storage bucket `brand-files` necesita config + RLS policies. `POST /api/v1/clients/{id}/brand-files` asume bucket existe · falla con 503 si no. Hoy bucket no creado en dashboard `rwlnihoqhxwpbehibgxu`. | (1) Crear bucket `brand-files` en Supabase Dashboard → Storage; (2) policy "Clients CRUD own files" para path `{client_id}/*`; (3) policy service_role full access; (4) public read si los archivos van a CDN (logos públicos) o signed URLs si privado; (5) MIME whitelist (pdf/png/jpg/svg/webp); (6) max size 10MB en backend ya enforced | 4h | Bajo (bloquea solo brand assets upload · wizard funciona sin assets) |
| DEBT-038 | **NUEVA (20 may 2026)**: Stripe Customer Portal embed pendiente en `SettingsPage > PaymentSection`. Hoy `src/components/settings/PaymentSection.tsx` muestra Card placeholder con botón disabled "Próximamente"; usuario no puede ver método de pago, cambiar tarjeta ni descargar invoices. Backend `bc_billing` no expone endpoint `/portal-session` (Stripe `billing_portal.Session.create`). Fase 3 §3.x | (1) Backend: nuevo endpoint `POST /api/v1/billing/create-portal-session` que invoca `stripe.billing_portal.Session.create(customer=client.stripe_customer_id, return_url=...)`; (2) Frontend: PaymentSection mutation → redirect `data.portal_url`; (3) Configurar Customer Portal en Stripe Dashboard (allowed actions: update payment method, download invoices, cancel subscription) | 6h | Medio (UX importante · pero plan base funciona via Checkout) |
| DEBT-037 | **CERRADA V1 client (22 may 2026 · Sprint 3)** via commit `2d90462`: `product_aria_premium_client` ($12/mes · sube `clients.aria_level +1` max 4) implementado completo. Cambios: (1) `config.py` +`stripe_price_aria_premium_client/_reseller` fields; (2) `bc_billing/domain/plan_pricing.py` +`ADDON_CODES` frozenset + `AddonCode` Literal + `get_price_id_for_addon()`; (3) NEW `bc_billing/application/create_aria_premium_checkout.py` (71L) con `has_active_aria_premium()` helper · check already_active vía `client_plans.addons` jsonb · Stripe Customer create-if-missing · metadata `{client_id, addon_code}`; (4) NEW `bc_billing/application/_addon_handlers.py` (62L) `handle_addon_activation` (push entry jsonb + bump aria_level) + `handle_addon_deactivation` (scan O(N) por subscription_id + reset aria_level a `_BASE_LEVEL[plan]`); (5) `_webhook_handlers.py` (87→98L) branchea `metadata.addon_code` en `on_checkout_completed` + `on_subscription_deleted` prueba `handle_addon_deactivation` primero; (6) NEW handler V3 `api/routes/billing_v3/handlers/upgrade_aria.py` (51L) POST `/api/v1/billing/upgrade-aria` · 409 already_active · 503 price_not_configured · 200 con `{checkout_url, session_id}`; (7) Frontend `ARIAUpgradeBanner.tsx` reemplaza botón disabled por `useMutation` real · onSuccess redirect `window.location.href = checkout_url` · toast destructive con descripción contextual. Storage: `client_plans.addons` jsonb (cero migration · ya existía en 00005). **Reseller variant (`product_aria_premium_reseller` $25/mes) → DEBT-046 nueva** (necesita migración `resellers.addons` col + refactor `_resolve_role` para reseller dynamic aria_level). **Original (histórico)**: ARIA Premium Stripe products no existían · banner disabled "Próximamente" · backend solo aceptaba target_plan basic/pro | — | 0h (cerrada V1) | — |
| DEBT-046 | **NUEVA (22 may 2026 · post DEBT-037 V1 cierre)**: ARIA Premium reseller variant (`product_aria_premium_reseller` $25/mes · sube reseller aria_level de 3 a 4 default). Spec §6.3 ARIA_NOVA_INTELLIGENCE define el producto pero V1 de DEBT-037 cubrió solo client path por scope discipline. Hoy `_resolve_role` en `use_aria_message.py` retorna hardcoded `3` para resellers · no consulta addons · y `resellers` table no tiene columna `addons` jsonb (cliente sí desde 00005) | Sprint 4 (~4h): (1) Migración `00019_resellers_addons.sql` ALTER TABLE resellers ADD COLUMN addons jsonb NOT NULL DEFAULT '[]'::jsonb; (2) Extender `_VALID_ADDONS_V1` en `create_aria_premium_checkout` con `aria_premium_reseller` + lookup en tabla resellers en vez de clients; (3) Refactor `_addon_handlers` para soportar ambos paths (client OR reseller según addon_code); (4) Refactor `_resolve_role` en use_aria_message para leer `resellers.addons` y bumpear nivel `min(3+1, 4) = 4` si aria_premium_reseller activo; (5) `upgrade_aria` handler detecta si user es reseller via repo y mapea a addon_code correcto; (6) Frontend ARIAUpgradeBanner ya funciona genéricamente con el $12/$25 según current_level pero necesita pasar context de role | 4h | Medio (UX upgrade ARIA reseller · client variant funciona) |
| DEBT-045 | **CERRADA PARCIAL (22 may 2026 · Sprint 3)** via commit `da63e75` + hot-fix `072948d`: cron horario `video_jobs_orphan_cleanup` (10mo job) ejecuta `cleanup_orphan_video_jobs()` (`bc_cognition/application/cleanup_orphan_video_jobs.py` 48L): `UPDATE video_generation_jobs SET status='failed', error='orphan_timeout', completed_at=now() WHERE status='running' AND started_at < now() - 15min` · WARNING log si encuentra orphans · INFO log si cero. Threshold 15min = 3x max Veo. **Persistent jobstore REVERTED** en hot-fix `072948d`: SQLAlchemy 2.0.25 (pin DEBT-012) INCOMPAT con Python 3.13.13 de Railway (AssertionError `SQLCoreOperations directly inherits TypingOnly but has additional attributes {'__static_attributes__', '__firstlineno__'}`). Local venv 3.11.9 no detectó el conflict. Scheduler revertido a memory store · jobs perdidos en Railway restart sigue siendo un riesgo · cubierto por DEBT-047 nueva. Bonus: `database_url` field en Settings se mantiene (cierra DEBT-029 partial · 1 site menos). DDD `X3` mantenido en 10 cron workers (cleanup cron sí está activo). **Beneficio parcial**: orphans en running >15min se limpian automáticamente · usuario ve "failed" en vez de "Generando…" infinito · max 1h15min de delay | — | 2h (cerrada parcial) | 4h pasaron a DEBT-047 |
| DEBT-047 | **NUEVA (22 may 2026 · post hot-fix `072948d`)**: Persistent jobstore APScheduler bloqueado por incompatibilidad SQLAlchemy 2.0.25 + Python 3.13.13 (Railway runtime). SQLAlchemy < 2.0.32 no soporta los nuevos `__static_attributes__` y `__firstlineno__` que introdujo Python 3.13. Hoy: scheduler usa memory jobstore · si Railway reinicia mid-cron, los timers configurados se pierden (deben re-registrarse en next startup_event que sí ocurre · pero jobs en running con state se pierden). Opciones de fix · 2 caminos: **(A) Bump SQLAlchemy a >=2.0.32**: necesita verificar compat con resto del stack · mem0ai estaba pinned para sqlalchemy<2.0.31 pero mem0ai está stubbed (DEBT-012) · low risk pero hay que probar. **(B) Pin Python 3.11 o 3.12 en Railway** vía runtime.txt o pyproject.toml: más seguro · 3.11 es lo que usamos local · puede ser cambio simple. Una vez compat resuelta · re-aplicar `AsyncIOScheduler(jobstores={"default": SQLAlchemyJobStore(url=settings.database_url)})` y revivir DEBT-045 full | Sprint 4 (~4h): probar opción A en branch separado · si rompe nada · merge · re-activar persistent jobstore en main. Backup plan: opción B si A causa ripples | 4h | Alto (UX video producción cuando Railway reinicia) |
| DEBT-044 | **CERRADA (22 may 2026 · Sprint 2)** via commit `ef6dee2`: migración 00017 (no 00016 como spec original · 00016 se usó para storage buckets en Sprint 2 P1) creó tabla `client_brand_dna(client_id PK FK clients ON DELETE CASCADE, dna_jsonb jsonb, score float, last_computed_at timestamptz, last_corpus_size int, created_at, updated_at)` + RLS (service_role ALL + authenticated SELECT solo su client) + **trigger SQL** `trg_invalidate_brand_dna AFTER INSERT/UPDATE/DELETE ON brand_voice_corpus FOR EACH ROW EXECUTE FUNCTION invalidate_brand_dna_on_corpus_change()` (SECURITY DEFINER · UPDATE client_brand_dna SET last_computed_at=NULL). Application: nuevo `bc_cognition/infrastructure/brand_dna_repository.py` (62L · fetch_persisted_dna + upsert + fetch_active_client_ids) · refactor `bc_cognition/application/use_brand_dna.py` (18→67L · read-through cache · stale threshold 24h · `async refresh_all_brand_dna()` para cron) · `bc_cognition/domain/brand_dna.py` ganó `to_dict()/from_dict()` puros (38→60L) para jsonb roundtrip · `backend/app/main.py` registra 9no cron `scheduler.add_job(refresh_all_brand_dna, 'cron', hour=3, id='brand_dna_refresh')` · `DDD_REGLAS_OMEGA.md X3` actualizado 8→9 cron workers con `brand_dna_refresh (3 AM diario)` en JOBS list. **Beneficios**: cache hit Anthropic alto (DNA estable día completo · cron 3am refresca proactivo · trigger invalida lazy cuando corpus cambia) · latencia P95 `/generate` reducida ~80ms (read tabla en vez de compute en hot path). **Original (histórico)**: Brand DNA Builder computaba on-demand cada request · ~50-100ms latency extra · rompía cache_control ephemeral cuando corpus cambiaba | — | 0h (cerrada) | — |
| DEBT-048 | **NUEVA (23 may 2026 · Sprint 2 closure · ①.B deferred)**: ARIA memory retrieval es cronológico (últimas N por `created_at DESC` vía `aria_memory_repository.fetch_recent_for_owner`) pero `ARIA_NOVA_INTELLIGENCE.md §5` (Context Builder V2) especifica **attention-based** — top-K por cosine similarity con la tarea actual vía pgvector `find_similar_memories(query_embedding, …, min_similarity=0.7)`. La RPC ya existe (migración 00002) y la columna `agent_memory.embedding vector(1536)` también, pero **cero código de embeddings vive en el repo · 100% de las rows tienen embedding=NULL**. Anthropic no provee embeddings (sugiere Voyage AI como partner oficial). Habilitarlo requiere **nueva I1 excepción explícita** porque hoy DDD_REGLAS_OMEGA.md §I1 solo permite Anthropic + Nano Banana (imagen) + Veo 3.1 (video). El impacto user-facing del gap: ARIA recuerda "lo último que hablaron" en vez de "lo más relevante a lo que estás preguntando ahora" · diferencia perceptible solo cuando la conversación cubre múltiples temas | Sesión dedicada futura (~16h): (1) Decisión owner explícita de agregar Voyage como I1 excepción #3 + actualizar `DDD_REGLAS_OMEGA.md §I1` + actualizar whitelist en `scripts/validate-before-push.sh`; (2) NEW `bc_cognition/infrastructure/voyage_adapter.py` aislado (≤75L · función `embed_text(text) -> list[float]` · modelo `voyage-3-lite` 512 dims O `voyage-3` 1024 dims · cuidado: schema actual asume 1536 · puede requerir ALTER COLUMN o pad/truncate strategy); (3) Decisión schema: ¿mantener vector(1536) y truncar/pad embeddings Voyage, o ALTER al dim nativo? Posible nueva migración 00020_agent_memory_embedding_dim; (4) Hook en `aria_memory_repository.insert_agent_memory` para embed + persistir embedding al INSERT (write-time · no backfill inicial); (5) Reemplazar `fetch_recent_for_owner` por `fetch_similar_for_owner(query_text, …)` que embed query + invoca RPC `find_similar_memories`; (6) Mantener fallback cronológico si embedding falla (best-effort · no romper conversación); (7) Backfill opcional Sprint posterior · vivir con (NULL OR not-NULL) en agent_memory durante transición; (8) Tests promptfoo eval comparando attention vs cronológico sobre fixtures conocidos; (9) Cost monitoring: Voyage-3-lite a $0.02/1M tokens → ~$0.02/cliente/mes estimado (1 embed por mensaje ARIA + 1 por INSERT new memory). **Por qué se difiere**: scope creció de "~60L · 1 archivo" a stack completo + contrato I1 + posible migración + cost stream nuevo. No procede en modo autónomo. Owner instruyó cerrar Sprint 2 con ②.A+②.B vivos y reservar embeddings para sesión propia | 16h | Medio (UX gap visible solo en conversaciones multi-tema · spec ARIA_NOVA §5 incumplida) |

| DEBT-VID-001 | **NUEVA (23 may 2026 · Sprint 3 · Video Pricing)**: Video Pack Stripe Checkout pendiente. Modal informativo cableado en `/content-lab` cuando `form.type === 'video'` (commit `d6b9a52`) muestra los 3 packs aprobados hoy (Starter $39/mes · Creator $95/mes · Cinematic Pro $125/mes) y los entitlements viven en `backend/app/bc_billing/domain/video_entitlements.py` (commit `8132628`), pero el botón "Activar Pack" lanza toast "Próximamente · contáctanos" porque no existe endpoint `POST /api/v1/billing/checkout-video-pack` ni Stripe Products creados. El cliente VE la oferta pero no puede self-serve la compra · workaround manual "contáctanos" funciona pero rompe el funnel | Sprint 4 (paraleliza arquitectura DEBT-037 cierre client variant): (1) Stripe Dashboard crear 3 products `prod_video_pack_starter/creator/cinematic_pro` con price_ids; (2) `Settings` añadir 3 fields `stripe_price_video_pack_*`; (3) extender `bc_billing/domain/plan_pricing.py` con `VIDEO_PACK_CODES` lookup paralelo a `ADDON_CODES`; (4) NEW `bc_billing/application/create_video_pack_checkout.py` (~70L) con `has_active_video_pack()` check + Stripe Customer create-if-missing + metadata `{client_id, video_pack_code}`; (5) NEW handler `api/routes/billing_v3/handlers/checkout_video_pack.py` POST `/billing/checkout-video-pack`; (6) `_addon_handlers.py` extender para video pack activation/deactivation (alimenta `client_plans.video_packs` jsonb O tabla nueva `client_video_subscriptions` según decisión schema); (7) Frontend `VideoAddonModal.handleActivate` reemplazar toast por `useMutation` real con `window.location.href = checkout_url`; (8) Decisión schema: ¿array en `client_plans.addons` jsonb (zero migration · sólo 1 pack activo a la vez) o tabla separada `client_video_subscriptions` (múltiples packs simultáneos permitidos)? Recomendación: opción A si product policy es "1 pack por cliente activo"; (9) Smoke E2E con Stripe test mode antes de prod | 8h (6h backend Stripe wiring + 1h frontend mutation + 1h smoke E2E) | Medio (UX upsell visible · cliente VE pero no puede comprar self-serve · workaround manual vivo) |

| DEBT-CL-020 | **NUEVA (23 may 2026 · Sprint 3 · UX paperclip always-visible)**: Paperclip 📎 ahora siempre visible en ContentLabFormV2 (todos los types) pero `<input type='file'>` `accept='image/*'` y MIME check defensivo con toast "Formatos adicionales próximamente · DEBT-CL-020" si el usuario fuerza otro formato. El cliente ESPERA poder adjuntar PDFs/docs/md (briefs, instrucciones, ejemplos, guías de marca) pero el backend no tiene el wiring · solo `/generate-image` acepta `reference_image_b64` desde UX-6 · `/generate` y `/generate-video` no tienen field reference_* en sus request models · cero extracción PDF/doc en backend (pypdf en requirements desde DEBT-039 pero sin handler que lo invoque). Además, incluso una imagen adjuntada con type=video o type=caption queda en `form.reference_image_b64` pero NUNCA se envía al backend (silent state preservation · solo type=image lo consume). | Sprint propio (~3h · scope cerrado): (1) `content_lab_models.py` +`reference_attachment_b64: Optional[str]` y `reference_mime_type: Optional[str]` en GenerateTextRequest + GenerateVideoRequest (GenerateImageRequest ya tiene reference_image_b64); (2) NEW `backend/app/api/routes/content_lab_v3/handlers/_attachment_extractor.py` (~80L · detecta MIME → ramifica: image_b64 retorna as-is · pdf → pypdf extract · docx → python-docx extract (NUEVA dep en requirements) · .md/.txt → base64 decode + read · cap 50k chars · 5MB raw); (3) `generate_text.py` extiende build_rafa_system para inyectar `\\n\\nCONTEXTO ADJUNTO DEL CLIENTE:\\n{texto extraído}` al system prompt cuando reference_attachment_b64 presente y mime non-image; (4) `generate_video.py` si attachment es imagen → pasa a Veo como reference (veo3_adapter ya lo acepta línea 50-54); (5) Frontend `PromptAttachmentControls` expandir accept a `image/*,video/*,.pdf,.md,.txt,.docx`, MIME detection en handleChange, pasar mime + base64 al hook · todos los 3 hooks pasarlo en payload | 3h | Medio (UX expectativa visible · pero el paperclip image-only ya cubre 80% de casos · documentación en hover suficiente hasta Sprint) |

**Total deuda estimada: ~651h (~16 semanas full-time)** · DEBT-004 subsumido por DEBT-017 (–60h estimadas); DEBT-012 no suma; DEBT-013 +16h; DEBT-014 +40h; DEBT-015 +20h; DEBT-016 +2h; DEBT-017 +80h; DEBT-018 0h (cerrada total 22 may · Sprint 2 P1); DEBT-019 0h (cerrada total 22 may · Sprint 2); DEBT-020 0h (cerrada total 22 may · Sprint 2); DEBT-021 +2h; DEBT-022 0h; DEBT-023 0h; DEBT-024 +12h; DEBT-025 +8h; DEBT-026 0h; DEBT-027 0h; DEBT-028 0h; DEBT-029 +6h; DEBT-030 +8h; DEBT-031 +4h; DEBT-032 0h (cerrada total 19 may); DEBT-033 +40h; DEBT-034 +16h; DEBT-035 +8h; DEBT-036 +8h; DEBT-037 0h (cerrada V1 client 22 may · Sprint 3 · reseller en DEBT-046); DEBT-044 0h (cerrada total 22 may · Sprint 2); DEBT-045 2h (cerrada parcial 22 may · cron cleanup vivo · persistent jobstore reverted post hot-fix); DEBT-046 +4h (nueva 22 may · reseller aria_premium variant); DEBT-047 +4h (nueva 22 may · persistent jobstore bloqueado por Python 3.13 + SQLAlchemy 2.0.25 incompat); DEBT-048 +16h (nueva 23 may · ARIA attention-based memory · stack embeddings · nueva I1 excepción); DEBT-VID-001 +8h (nueva 23 may · Sprint 3 · Video Pack Stripe Checkout wiring · modal informativo vivo · entitlements vivos · solo falta Stripe layer); DEBT-CL-020 +3h (nueva 23 may · Sprint 3 · paperclip always-visible · extracción PDF/doc/md backend para inyección al system prompt).

**Hitos 23 may 2026 (Sprint 2 cierre):** Backend `brand_voice_v2` desplegado (commit `de8e7b7`): `GET /api/v1/brand-voice/summary` retorna `{corpus_count, latest_approvals[5], top_keywords[10]}` desde `brand_voice_corpus` filtrado por JWT del cliente. Capas DDD A1/A9 con cada archivo ≤75L. Frontend `/brand-voice` desplegado (commit `d2b2d05`): rewrite de `BrandVoicePage.tsx` (12L stub `ComingSoon` → 54L real) + hook `useBrandVoiceSummary` con React Query + 3 componentes (BrandVoiceStats / LatestApprovals / TopKeywords). Solo lectura · sin botones edit · empty states explican que ARIA aprende de cada aprobación en Content Lab. Sprint 2 objetivo ① (ARIA lee `agent_memory` al inicio) confirmado vivo desde T4 Sprint 1 (cronológico últimas-10 vía `_aria_memory_context.py` + tests pasando). Sprint 2 objetivo ①.B (upgrade attention-based attention con pgvector) **diferido** a sesión propia → DEBT-048 nueva con scope completo (Voyage AI + nueva I1 excepción + posible migración schema embedding dim). Total deuda: ~624h → ~640h.

**Hitos 23 may 2026 (Sprint 3 · Video Pricing arranque):** Decisión pricing video aprobada por owner (Básico 1×8s lifetime cebo · PRO 2×8s/mes · Starter $39/6×8s · Creator $95/5×30s · Cinematic Pro $125/3×60s · sin videos sueltos). 3+1 commits desplegados: (1) `a3dbb7c` docs MODELO_NEGOCIO §4.4 con tabla packs + margenes API documentados; (2) `8132628` feat `bc_billing/domain/video_entitlements.py` 67L capa pura con MappingProxyType inmutable + 6 self-check asserts al import (patrón limits_omega · zero pytest infra); (3) `1aba7be` feat `src/components/addons/VideoAddonModal.tsx` 57L + `VideoPackCard.tsx` 39L + `_video_packs_data.ts` 48L con 3 cards comparativas + botón amber "Activar Pack"; (4) `d6b9a52` feat wire `<VideoAddonModal />` en `ContentLabFormBar` cuando `form.type === 'video'` (45L · short-circuit React · cero impacto en otros tipos). `limits_omega.py` intacto (decisión P1=A · semánticamente correcto · zero ceremony SHA1/test-first). Pendiente Stripe wiring → DEBT-VID-001 nueva (8h Sprint 4). Total deuda: 640h → 648h.

**Hitos 19 may 2026 (Sesión ARIA Fase 1):** Backend ARIA bc_billing fase 1 desplegado (migración 00008 + bc_cognition.persona_aria + api/routes/aria_v1/ con message/history/track endpoints). Frontend ARIA fase 1 desplegado (ARIAContext + useARIAChat + useBehavioralTracking + ARIAButton header + ARIADrawer 380px shadcn Sheet). Behavioral tracking activo en Dashboard mount + ARIA opened. 224→227 routes uvicorn (3 ARIA endpoints registrados). DEBT-037 nueva (ARIA Premium Stripe products pending). Total deuda: 642h → 650h.

**Hitos 18 may 2026:** Backend uvicorn local arranca limpio. `/health` → 200, `/docs` → 200, `/openapi.json` → 200, 223 routes registrados. Bundle de 5 DEBTs cerradas + 2 nuevas registradas (DEBT-029/030) para Fase 3. Próximo paso: smoke E2E con frontend Vite + dashboard preview.

## SECCIÓN 7 — STACK CONFIRMADO

```
FRONTEND       Vite 5 + React 18 + TypeScript 5.8 + shadcn/ui + Tailwind
               React Query 5 · React Router 6 · React Hook Form + Zod
BACKEND        Python 3.11 + FastAPI 0.109 + Pydantic 2 + SQLAlchemy 2
               Supabase Python SDK 2.7 · APScheduler · BeautifulSoup4 · pypdf
IA TEXTO       Anthropic SDK 0.34+ · claude-haiku-4-5-20251001
                                     claude-sonnet-4-6
                                     claude-opus-4-7
IA IMAGEN      google-genai · gemini-3.1-flash-image-preview (Nano Banana 2)
IA VIDEO       google-genai · veo-3.1-generate-preview (Veo 3.1)
DB             Supabase (PostgreSQL 15 + pgvector + auth + storage + RLS)
DEPLOY FRONT   Vercel (un solo proyecto)
DEPLOY BACK    Railway (nixpacks → uvicorn)
SECRETS        .env local · Railway env vars · Vercel env vars
OBSERV LLM     Langfuse (pendiente integrar)
TESTING        Vitest (frontend) · Pytest (backend) · Promptfoo (cognition)
```

## SECCIÓN 8 — IDENTIDAD GIT

```
SETUP DUAL EN ESTA MÁQUINA (verificado arranque 17 may 2026)
──────────────────────────────────────────────────────────────────
Proyecto          Ruta local              Gitconfig file
──────────────    ──────────────────────  ──────────────────────────────
OmegaRaisen       D:\Omega Master redes\  ~/.gitconfig-omegamaster ← ESTE
                                            user.name  = raisenomega
                                            user.email = raisenagencypr@gmail.com

Raisen Omega      D:\Raisen Omega\        ~/.gitconfig-raisen      ← LEGACY
(otro proyecto)                            NO MODIFICAR
──────────────────────────────────────────────────────────────────
```

Ambos bloques `[includeIf]` coexisten en `C:\Users\muscl\.gitconfig`.
Ver `IDENTIDAD_GIT_CRITICA.md` §1 + `PROTOCOLO_IDENTIDAD_GIT_OMEGA.md`.

---

## SECCIÓN 9 — SESIÓN 1 CONTENT LAB · 23 may 2026 · CERRADA

### Estado del sistema post-Sesión 1

**Content Lab funcional end-to-end con cliente real en producción.**

**Backend** (`omega-production-3c67.up.railway.app`):
- `POST /api/v1/content-lab/generate` · Claude 4.x + RAFA persona + Brand DNA + virality score
- `POST /api/v1/content-lab/generate-image` · Nano Banana → Supabase Storage persistente
- `POST /api/v1/content-lab/generate-video` + `GET .../{job_id}` · Veo 3.1 con asyncio.create_task
- `PATCH /api/v1/content/{id}/save` · alimenta brand_voice_corpus
- `POST /api/v1/calendar/schedule/` · scheduled_posts INSERT

**Frontend** (`omegaraisen.agency`):
- `/content-lab` UI V2 con 3 generaciones reales · 3 CTAs cableados · block builder dinámico
- 8 hooks especializados consumiendo `src/lib/api-client.ts` consolidado
- Modal Agendar libertad total (≥3 piezas combo · sin slots fijos)

**Stack actualizado:**
```
google-genai==2.6.0      (Veo 3.1 generate_videos + Nano Banana)
supabase==2.18.1         (httpx<0.29 compat · realtime 2.7.0)
httpx==0.28.1            (requerido google-genai 2.x)
pydantic==2.11.7         (requerido realtime 2.7.0)
```

### DEBTs nuevas (CL-003 a CL-018)

11 activas · 1 cerrada (CL-014) · 1 verificar (CL-012).
Cleanup estimado: ~6-8h en próximas sesiones.

**Alta urgencia:**
- ~~DEBT-CL-016 · `ClientProfile` model desincronizado de DB~~ ✅ **CERRADA 23 may 2026** (Sprint 3 · `PlanOption` +'adopcion' · 6 fields → Optional null-tolerant · `useMyClients` restaurado a `apiGet`)

**Media urgencia:**
- ~~DEBT-CL-005 · backend ignora client_id del frontend (usa user JWT)~~ ✅ **CERRADA 23 may 2026** (Sprint 3 · NEW `_client_resolver.resolve_client_or_403` · 3 handlers POST + GET status video usan resolver/ownership · frontend manda `client_id` en payload de los 3 hooks)
- DEBT-CL-008 · `/generate-image` hardcoded 1024x1024
- ~~DEBT-CL-011 · Nano Banana ImageConfig (re-activar en 2.6.0)~~ ✅ **CERRADA 23 may 2026** (Sprint 3 · `types.ImageConfig(aspect_ratio=...)` cableado en GenerateContentConfig · `_VALID_ASPECT_RATIOS` frozenset defensivo · aspect honrado end-to-end UI→SDK)
- ~~DEBT-CL-013 · useScheduleBlock bypassa backend RBAC~~ ✅ **CERRADA 23 may 2026** (Sprint 3 · opción C · cerrados los 4 endpoints calendar legacy con `get_current_user` + ownership via NEW `calendar/_access.py` · frontend `useScheduleBlock` elimina query Supabase directo · schedule_post acepta `client_id+platform` además de `account_id` legacy)
- ~~DEBT-CL-015 · account_id resolución sin elección del user~~ ✅ **CERRADA 23 may 2026** (Sprint 3 · NEW `GET /api/v1/clients/{id}/social-accounts` + `useMyAccounts` hook · dropdown "— Cuenta —" en form bar cuando N>1 cuentas/platform · backend `social_account_id: Optional` con `resolve_account_by_id_or_403` · **BONUS fix latente**: removido `ORDER BY is_primary` (col inexistente en schema V3) de `calendar/_access.py` + `calendar_v3/_access.py` · ahora filtra `status='active'` + `ORDER BY created_at`)
- ~~DEBT-CL-017 · backend ScheduledPostCreate sin video_url field~~ ✅ **CERRADA 23 may 2026** (Sprint 3 · path X · NEW `POST /api/v1/calendar-v3/schedule/` con schema V3 real + `media_url` único col nueva migración 00020 · handler legacy `calendar/schedule_post.py` deprecated · frontend `useScheduleBlock` apunta al V3 · DEBT-031 partial close)

Detalle completo: `PENDIENTES_Y_PROGRESOS_20260523.md`.

### Próxima Sesión 2

Sprint 1 PLAN_IMPLEMENTACION:
1. Brand DNA Builder (visual UI)
2. ARIA memory injection wiring
3. prompt_vault seed (30 prompts production-tested)

Pre-requisito ~~recomendado: cerrar DEBT-CL-016 (~45 min)~~ ✅ **CERRADA 23 may 2026 · Sprint 3**.

---

> **Regla:** Si está en "lo que existe" pero no puedes mostrar el archivo
> de código donde vive → se mueve a "no existe". Sin excepciones.
> **Última actualización:** 23 mayo 2026 (Sprint 3 Video Pricing) · firmado: Claude (cierre Sesión 1 Content Lab + Sprint 3 Video) + Ibrain (CEO)
