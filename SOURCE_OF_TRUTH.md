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
| DEBT-018 | Imágenes generadas por Nano Banana se devuelven como **data URIs** (`data:image/png;base64,XXX`) vía `bc_cognition/infrastructure/_image_compat.py`, no como URLs hospedadas | Hot-swap §2.4 (18 may 2026) split en 2 commits: commit 1 = compat layer + data URIs · commit 2 = Supabase Storage upload. Data URIs son pesados (>1MB c/u), no aptos para guardar en DB ni compartir en redes sociales. Bloqueante antes de deploy producción. **Cerrar en sesión §2.4b**: crear bucket `generated-images/` en Supabase + RLS público read / service_role write + reemplazar return en `_image_compat.py` por `supabase.storage.from_('generated-images').upload(...)` retornando URL pública | 6h | Crítico antes prod |
| DEBT-019 | Videos generados por Veo 3.1 se persisten como **URIs temporales de Google** (TTL · mueren en minutos/horas) vía `bc_cognition/infrastructure/_video_compat.py`. `content_lab_generated.content` queda con URLs muertas tras TTL | Hot-swap §2.5 (18 may 2026) opción A: sync wrapper + URI temporal. Data URIs no viables para video (5-50MB c/u). **Cerrar en sesión §2.5b**: extender storage helper de DEBT-018 a video, descargar bytes del `video_uri` antes de TTL + `supabase.storage.from_('generated-videos').upload(...)` + reemplazar return en `_video_compat.py` por URL pública persistible | 6h | Crítico antes prod |
| DEBT-020 | `_video_compat.generate_video_compat()` hace `await poll(max_wait_s=300)` sincrónicamente dentro del endpoint HTTP `/generate-video-runway/`. Veo 3.1 tarda 30-90s típicamente — riesgo de timeout en Vercel (10-30s) y Railway (varios minutos OK pero degrada throughput) | Hot-swap §2.5 (18 may 2026) opción A: sync wrapper. Plan §R5 anticipa "UI con polling. Background job pattern" como mitigación. **Cerrar en Fase 3**: implementar job queue (APScheduler ya disponible) → `POST /generate-video` retorna `{job_id, status:pending}` inmediato + worker async hace start+poll + `GET /generate-video/{job_id}` retorna estado/URL al completarse + frontend con polling | 16h | Alto (UX + reliability) |
| DEBT-021 | Endpoint `/generate-video-runway/` y handler `handle_generate_video_runway` mantienen el nombre "runway" aunque internals ahora usan Veo 3.1. Frontend Lovable llama `/generate-video-runway/` — renombrar rompería contrato API | Hot-swap §2.5 (18 may 2026): "lift & shift" preserva contrato externo. **Cerrar durante Fase 3 §3.2 refactor por bounded context**: renombrar endpoint a `/generate-video/` + handler a `handle_generate_video` + actualizar frontend Lovable coordinadamente | 2h | Bajo (cosmético) |
| DEBT-022 | **CERRADA en §2.6 (18 may 2026)**: extendido `_image_compat.generate_image_compat()` con `reference_images_b64: Optional[List[str]] = None`. `generate_image.py` simplificado a single-path Nano Banana (`_generate_with_nano_banana` para generate y edit). `import fal_client` eliminado. 0 referencias a FAL en backend | — | 0h (cerrada) | — |
| DEBT-023 | **CERRADA (18 may 2026)**: `claude_service.model` bumped a `claude-sonnet-4-6`. También actualizado el string del response en `services/llm/router.py:LLMResponse.model`. Long-term routing dinámico por agent_code sigue cubierto por DEBT-024 | — | 0h (cerrada) | — |
| DEBT-024 | 48 callers de `claude_service.generate_text()` (drop-in §2.6 desde openai_service) siguen usando el wrapper Lovable en `infrastructure/ai/claude_service.py`. V3 manda que `bc_cognition/infrastructure/anthropic_adapter.py` sea el ÚNICO entry point a Claude. Hay duplicación con duplicate caching/timeout logic ausente en claude_service | Migración Fase 3 §3.2: cada bounded context refactoriza sus agents para llamar `anthropic_adapter.generate(agent_code=..., system=..., messages=...)` retornando Result<T,E>. Crea `_text_compat.py` si conviene mantener signature legacy durante transición. Eventualmente eliminar `claude_service.py` | 12h | Medio (DDD ÚNICO entry) |
| DEBT-025 | `services/ai_providers.py` + `services/llm/router.py` + `infrastructure/ai/agent_dispatcher.py` + `agent_registry.py` siguen vivos tras §2.6 con refactor mínimo (solo Anthropic). Duplican funcionalidad de `bc_cognition.domain.routing_table` + `bc_cognition.infrastructure.anthropic_adapter` V3 | Refactor Fase 3 §3.2: unificar el routing layer con bc_cognition V3. Eliminar agent_dispatcher/agent_registry o convertirlos en thin wrappers sobre routing_table. Actualizar callers que importan `AIProviders` / `generate_content` del router | 8h | Medio (consolidación) |

**Total deuda estimada: ~564h (~14 semanas full-time)** · DEBT-004 subsumido por DEBT-017 (–60h estimadas); DEBT-012 no suma; DEBT-013 +16h; DEBT-014 +40h; DEBT-015 +20h; DEBT-016 +2h (post-§2.6, antes 4h · solo C2); DEBT-017 +80h; DEBT-018 +6h; DEBT-019 +6h; DEBT-020 +16h; DEBT-021 +2h; DEBT-022 0h (cerrada §2.6); DEBT-023 0h (cerrada model bump); DEBT-024 +12h; DEBT-025 +8h.

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

> **Regla:** Si está en "lo que existe" pero no puedes mostrar el archivo
> de código donde vive → se mueve a "no existe". Sin excepciones.
> **Última actualización:** 17 mayo 2026 · firmado: Claude (auditor) + Ibrain (CEO)
