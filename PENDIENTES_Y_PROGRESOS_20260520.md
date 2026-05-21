# PENDIENTES_Y_PROGRESOS · 20 mayo 2026

> Contexto de arranque para la próxima sesión · NO es gitignore · se commitea.

---

## 1. Resumen ejecutivo del día

Sesión maratónica. **5 pages del frontend Lovable** reescritas contra schema V3 real (DEBT-033 CERRADA TOTAL). **3 endpoints v3 bounded contexts** creados (clients_v3, content_v3, calendar_v3). **3 migraciones** aplicadas (00011, 00012, 00013). **4 hotfixes producción**: CORS, JWT auth (HS256 → JWKS ES256/RS256), 500 endpoints content/calendar (PostgREST embed + schema mismatch). **Settings V2** con 6 tabs chip navigation + avatar upload. **Analytics V2** con P1 strict (cero mock data). **Wizard onboarding** completo + edit pre-poblado. **Reuso** del PillGroup component en 8+ lugares.

**29 commits hoy** · todos validate 10/10 · cero violaciones C1/A2/I1.

---

## 2. Commits del día

```
7321f63 refactor(aria): split aria_repository (100L) en 2 archivos <=75L (C4)
863e2aa feat(settings): Settings V2 · 6 tabs + avatar upload + operator profile + notifications
13c7e48 fix(analytics): P1 no mock data + remove scrollbar
eda7ac5 fix(analytics): growth ascending + engagement data + heatmap redesign to bars
a0ce918 refactor(analytics): Analytics V2 compact layout + heatmap fix (DEBT-034 UI)
a0e30a1 fix(content+calendar): 500 root cause · schema real difiere · mapeo cols correctas
d8c46ae fix(content): GET /content/ 500 · evita PostgREST embed (mismo patrón calendar)
28b7e1c fix(calendar): GET /calendar 500 · evita PostgREST JOIN ambiguity con fetch+merge
361b923 fix(auth): JWT validation via JWKS (ES256/RS256) · Supabase Signing Keys
0a6324e fix(auth): JWT validate Supabase first · fallback local (401 prod fix)
728bc06 fix(cors): backend lee BACKEND_CORS_ORIGINS env (ignora hardcode previo)
a5f6ddd feat(calendar): Calendar V3 page + status endpoints (DEBT-033 CERRADA)
eb61136 feat(content): Content V3 page + save/unsave endpoints (DEBT-033 parcial)
8b3625c feat(onboarding): error state + retry button cuando GET falla
8ecd1b9 fix(onboarding): SectionSamples placeholder literal \n -> single-line
78504f5 feat(clients): edit opens full wizard pre-populated + GET/PATCH onboarding
6c8aae5 fix(onboarding): accounts order + logo upload + region labels + age freetext
e5ef8f3 fix(onboarding): single-line pills + tone unlimited + goals multi3
e49adbf fix(onboarding): regions pills + compact inputs + tone inline + banner inline
0a96569 refactor(onboarding): PillGroup + layout global + modal resize
bc1c8ea refactor(onboarding): fullscreen modal + global compact + section fixes
edf367e fix(aria): import Any in aria_repository (Railway boot crash · NameError)
88e3074 fix(onboarding): fixed modal height + compact sections + social split-panel
697fab7 fix(onboarding): free navigation + persist state + region multi-select
edbb225 refactor(onboarding): horizontal stepper UI + section-by-section navigation
ab90076 feat(onboarding): Wizard Nuevo Cliente V3 frontend (DEBT-033 mayor close · DEBT-041 cerrada)
ecd35a7 feat(clients_v3): onboarding wizard backend + schema 00011 (DEBT-039/040/041 nuevas)
130cc48 feat(clients_v3): PATCH /profile + Settings page V3 (DEBT-033 parcial · DEBT-038 placeholder)
bc78f4b chore(compliance): routing_table tests + sync ARIA entries to contract docs (X2 audit)
```

---

## 3. Estado de producción al cierre

| Componente | URL / Identificador | Estado |
|---|---|---|
| Frontend Vercel | `https://omega-two-wine.vercel.app` | UP · auto-deploy desde main |
| Backend Railway | `https://omega-production-3c67.up.railway.app` | UP (después de los 4 hotfixes prod) |
| Supabase Project | `rwlnihoqhxwpbehibgxu` (Omega MR) | UP · 13 migraciones aplicadas |
| Bucket `brand-files` | Supabase Storage | UP · 10MB · png/jpg/webp/svg/pdf · 3 RLS policies (DEBT-041 cerrada) |
| Bucket `avatars` | Supabase Storage | UP · 5MB · png/jpg/webp/gif · 3 RLS policies (00013) |
| 236 routes registrados | FastAPI uvicorn | Boot OK · auth JWKS funcionando |

### Funciona
- Auth: Supabase JWT (ES256 RS256 vía JWKS) + fallback local HS256
- CORS: lee `BACKEND_CORS_ORIGINS` env (CSV parsed)
- `/api/v1/clients/{profile,onboarding,{id}/brand-files,{id}/parse-brand-pdf,{id}/onboarding-data}` (5 endpoints clients_v3)
- `/api/v1/content/` GET + PATCH `/{id}/save` (mapeado a schema real: generated_text, status, agent_code)
- `/api/v1/calendar/` GET + PATCH `/{id}/status` (mapeado: scheduled_for único timestamptz, status enum)
- `/api/v1/aria/{message,history,track,history DELETE}` (4 endpoints)
- Wizard onboarding completo (10 secciones) + edit pre-poblado del cliente
- Settings V2 con 6 tabs (Perfil/Plan/ARIA/Cuentas/Seguridad/Notificaciones)
- Avatar upload reactivo a sidebar

### Stubs / parcial
- `/api/v1/clients/{id}/parse-brand-pdf` retorna 501 (DEBT-039 · pypdf + Haiku Fase 3)
- PaymentSection · form visual disabled (DEBT-038 · Stripe Customer Portal pendiente)
- ARIA Premium upgrade · botón disabled (DEBT-037)
- OAuth conectar cuentas sociales · botón disabled (DEBT-040)
- Reportes ARIA descargables · botón disabled (DEBT futura)
- Bell notifications · decorativo solo (DEBT-035)

### Bugs conocidos sin fix
- Analytics: P1 strict aplicado · todas las tarjetas muestran "—" hasta que llegue Meta API (DEBT-034)
- `/api/v1/analytics/dashboard/` retornaría 500 si se invoca (refs tablas inexistentes · DEBT-031 parcial)

---

## 4. DEBTs cerradas hoy

| ID | Detalle |
|---|---|
| **DEBT-031** (parcial) | `client_context` ya existe via migración 00011 · resta `agent_executions` + cols incorrectas en handler legacy |
| **DEBT-033** (TOTAL) | 5 pages Lovable rewriteadas contra V3: Content/Calendar/Settings/Clients/ClientDetail |
| **DEBT-041** (TOTAL) | Bucket `brand-files` creado · 3 RLS policies aplicadas vía migración 00012 |

---

## 5. DEBTs nuevas hoy

| ID | Descripción | Horas est |
|---|---|---|
| DEBT-038 | Stripe Customer Portal embed pendiente en PaymentSection | 6h |
| DEBT-039 | PDF parser onboarding (pypdf + Haiku auto-populate client_context) | 12h |
| DEBT-040 | OAuth flows por plataforma (Meta MCP Fase 2) | 40h |
| DEBT-042 | `clients.region` TEXT vs `regions list[str]` · CSV-joined hoy | 3h |
| DEBT-043 | Sin índice composite `content_lab_generated(client_id, status)` | 1h |

**Total deuda nueva**: +62h

---

## 6. Próxima sesión · orden de prioridades

```
P0 · Content Lab (corazón del sistema)
     - Leer legacy backend/app/agents/ + content_lab/ routes
     - Reescribir generación de contenido contra content_lab_generated V3
     - Endpoints POST /content-lab/generate (text/image/video)
     - Integrar con brand_voice_corpus aprobados
     - UI: nuevo Content Lab page (no es Content.tsx · ese es review)

P1 · Brand Voice
     - Endpoint análisis: GET /brand-voice/profile/{client_id}
     - Retorna tone_tags + keywords + samples del corpus
     - UI: BrandVoiceCard en Dashboard con score + sugerencias

P2 · Crisis Room
     - Endpoint POST /crisis/scan · monitorea menciones
     - Integrar con SENTINEL agent
     - UI: CrisisRoom page · alertas + draft responses

P3 · Dashboard Reseller
     - Reseller ve aggregate de todos sus clientes
     - Endpoint GET /reseller/{id}/dashboard
     - UI: ResellerDashboard distinto al ClientDashboard

P4 · Bell notifications real
     - Crear tabla `notifications` (user_id, type, payload, read_at)
     - Endpoint GET /notifications/{count,list,mark-read}
     - Bell.tsx lee endpoint · usa localStorage notification_prefs (ya guardado)
     - DEBT-035 reabre con scope claro

P5 · DEBT-037 ARIA Premium
     - 2 productos Stripe ($12/$25)
     - Extender bc_billing con upgrade_aria_premium use case
     - ARIAUpgradeBanner pasa de disabled a mutation real
```

---

## 7. Migraciones aplicadas

```
00001_initial_consolidated.sql        (base schema · pre-sesión)
00002_agent_memory_pgvector.sql       (pre-sesión)
00003_rls_complete.sql                (pre-sesión)
00004_anti_fraud_signals.sql          (pre-sesión)
00005_*.sql                           (pre-sesión)
00006_*.sql                           (auto-create client trigger · pre-sesión)
00007_*.sql                           (Stripe webhooks + idempotencia · pre-sesión)
00008_aria_intelligence_schema.sql    (behavioral_events, brand_voice_corpus · pre-sesión)
00010_behavioral_events_reseller_id   (ARIA Fase 1 · pre-sesión)
00011_client_onboarding_schema.sql    ← HOY · client_context (43 cols) + client_brand_assets + social_accounts +11 cols + brand_files +3 cols
00012_brand_files_storage_bucket.sql  ← HOY · bucket brand-files + 3 RLS storage.objects
00013_avatars_bucket.sql              ← HOY · bucket avatars + 3 RLS storage.objects
```

---

## 8. Variables de entorno producción (keys · no values)

### Railway backend
```
ENVIRONMENT, DEBUG, APP_NAME, APP_VERSION
SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
SUPABASE_JWT_SECRET                   (obsoleta · JWKS ES256 reemplaza · safe to remove)
DATABASE_URL, SUPABASE_DB_PASSWORD
SECRET_KEY, JWT_SECRET_KEY            (JWT_SECRET_KEY usado por /auth/login legacy fallback)
JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
ANTHROPIC_API_KEY
GEMINI_API_KEY                        (Nano Banana + Veo 3.1)
STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
STRIPE_PRICE_BASIC, STRIPE_PRICE_PRO
BRAVE_API_KEY                         (web search MCP)
RESEND_API_KEY, EMAIL_FROM
BACKEND_CORS_ORIGINS                  (CSV · debe incluir omega-two-wine.vercel.app)
ALLOWED_HOSTS
LOG_LEVEL, ENABLE_BACKGROUND_WORKERS, WORKER_TIMEZONE
ESCALATION_EMAIL, ESCALATION_THRESHOLD_SENTINEL
```

### Vercel frontend
```
VITE_SUPABASE_URL
VITE_SUPABASE_PUBLISHABLE_KEY
VITE_API_URL                          (https://omega-production-3c67.up.railway.app/api/v1)
VITE_APP_ENV                          (production)
```

### NO requeridas (deprecadas)
- `SUPABASE_JWT_SECRET` — JWKS reemplazó · field default empty en config

---

## 9. Usuarios de prueba

> No documentados explícitamente en esta sesión. La próxima sesión debe:
> 1. Crear test user vía Supabase Dashboard Auth · seed datos vía trigger auto
> 2. Documentar email + password en este doc (o vault separado)
> 3. Idealmente 2 users: 1 cliente + 1 reseller para probar access control

---

## 10. Notas para la próxima sesión

- **Protocolo obligatorio** preserved en `~/.claude/memory/feedback_omega_pre_task_protocol.md`: leer CLAUDE.md + SOURCE_OF_TRUTH.md + DDD_REGLAS_OMEGA.md + ARIA_NOVA_INTELLIGENCE.md antes de cualquier código.
- **PillGroup reusable** en `src/components/onboarding/PillGroup.tsx` · usado en 8+ lugares.
- **safe_insert pattern** (audit FIX 4) usado en aria_repository · clients_v3 · content_v3 · calendar_v3. Replicar en nuevos bounded contexts.
- **PostgREST embed evitar** en queries con JOIN ambiguity · usar pattern fetch+merge (ver calendar_v3 y content_v3 readers).
- **Schema real ≠ spec** en varias tablas. ANTES de escribir handlers verificar columnas con `grep "CREATE TABLE X" supabase/migrations/`.
- **Migration apply**: `supabase db push --linked` ya configurado · CLI autenticado.

---

**Cierre 20 may 2026** · firmado: Claude Code (sesión maratónica) + Jorge Ibrain (CEO Raisen).
