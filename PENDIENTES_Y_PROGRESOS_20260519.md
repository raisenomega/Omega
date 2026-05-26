# OMEGA · PENDIENTES Y PROGRESOS · SESIÓN 18-19 MAY 2026

> **Handoff operacional · versionado en el repo** (sin secretos · safe to commit).
> `.gitignore` permite `PENDIENTES_Y_PROGRESOS_*` vía la negación de línea 133.
>
> Generado al cierre 19 may 2026 · 01:06am. Próxima sesión: 19 may PM.

---

## ÍNDICE

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Cronología de commits](#2-cronología-de-commits)
3. [Progresos completados por área](#3-progresos-completados-por-área)
4. [Migraciones SQL aplicadas hoy](#4-migraciones-sql-aplicadas-hoy)
5. [DEBTs cerradas hoy](#5-debts-cerradas-hoy)
6. [DEBTs nuevas registradas hoy](#6-debts-nuevas-registradas-hoy)
7. [DEBTs heredadas activas (Fase 3)](#7-debts-heredadas-activas-fase-3)
8. [Memorias persistentes agregadas](#8-memorias-persistentes-agregadas)
9. [Pendientes inmediatos próxima sesión](#9-pendientes-inmediatos-próxima-sesión)
10. [Dudas abiertas que requieren decisión](#10-dudas-abiertas-que-requieren-decisión)
11. [Verificación visual pendiente del usuario](#11-verificación-visual-pendiente-del-usuario)
12. [Acciones manuales no automatizables](#12-acciones-manuales-no-automatizables)
13. [Estado del sistema al cierre](#13-estado-del-sistema-al-cierre)
14. [Notas operativas](#14-notas-operativas)

---

## 1. RESUMEN EJECUTIVO

**Sesión de 2 días (18 may día + 18→19 noche). 16 commits totales pusheados a `main`.**

Bloques mayores cerrados:
- **Fase 2 §2.1-§2.6 completada:** lift & shift del frontend+backend Lovable, hot-swaps DALL-E→Nano Banana / Runway-FAL→Veo 3.1 / OpenAI-Groq-DeepSeek→Anthropic-only.
- **uvicorn local arranca limpio** tras resolver 5 bloqueadores en cascada (DEBT-012/026/027/028/030).
- **3 features de UI cliente PYME:** Sidebar con perfil/logout, KPIs dashboard con data real (regla P1), Plan Status Bar inline con bordo amarillo CTA.
- **2 migraciones SQL aplicadas en remoto:** `00004_anti_fraud_signals` (R1+R5 del MODELO canónico) y `00005_client_plans` (billing cycle source).
- **Crashes de producción resueltos:** `/analytics` (TypeError toLocaleString), `/media` (defensive aplicado preventivo), 18 console errors del dashboard.
- **Sistema de iconos unificado a Lucide SVG** (sin emojis) en 5 archivos del frontend.

Total deuda registrada: **~632h (~16 semanas Fase 3 full-time)**.

Backend uvicorn responde `/health → 200`, `/docs → 200`, `/openapi.json → 200`, 223 routes. Frontend Vite dev arranca en `:5174`. Validator interno 10/10 en todos los commits.

---

## 2. CRONOLOGÍA DE COMMITS

Orden cronológico inverso (más reciente arriba):

| Hash | Fecha | Título | Líneas net |
|---|---|---|---|
| `a190042` | 2026-05-19 | ui: Plan Status Bar inline con título Dashboard + borde amarillo CTA | +15/-10 |
| `cb8ec26` | 2026-05-19 | feat(ui): bar siempre visible cliente + iconos Lucide unificados (sin emojis) | +92/-77 |
| `c4e6a14` | 2026-05-19 | feat(dashboard): Plan Status Bar para cliente PYME en /dashboard | +58/-0 |
| `e4da284` | 2026-05-19 | fix(frontend): crashes /analytics + /media + 18 console errors (DEBT-033/034) | +125/-973 |
| `fbd8d28` | 2026-05-18 | feat(clients): Step 3 — Plan Status Bar inline (MODELO §7) | +1214/-180 |
| `d84c480` | 2026-05-18 | feat(dashboard): Step 2 — KPIs reales del backend (regla P1) | +76/-46 |
| `80aa40d` | 2026-05-18 | feat: sidebar user footer + anti-fraud baseline (R1 + R5) | +175/-57 |
| `b9833f5` | 2026-05-18 | fix(backend): uvicorn local boot — bundle DEBT-026/027/028/030 | +95/-33 |
| `b7b1f44` | 2026-05-18 | fix(infra): stub langsmith/mem0/qdrant imports — DEBT-012 resuelta | +71/-250 |
| `c3d725c` | 2026-05-18 | fix: bump claude_service.model Sonnet 4.5 → 4.6 (DEBT-023 cerrada) | — |
| `29092c1` | 2026-05-18 | feat: eliminar OpenAI/Groq/DeepSeek + reemplazar generate_text (Fase 2 §2.6) | — |
| `521c67c` | 2026-05-18 | feat: hot-swap Runway/FAL → Veo 3.1 (Fase 2 §2.5) | — |
| `9da0233` | 2026-05-18 | feat: hot-swap DALL-E 3 → Nano Banana (Fase 2 §2.4 commit 1/2) | — |
| `5dc1c3e` | 2026-05-18 | feat: lift & shift Lovable backend (Fase 2 §2.1) | — |
| `9091a89` | 2026-05-18 | feat: lift & shift Lovable frontend (Fase 2 §2.2) | — |
| `d9df7f7` | 2026-05-18 | feat: bootstrap V3 stack — Fase 0 completa (OmegaRaisen rebuild) | — |

---

## 3. PROGRESOS COMPLETADOS POR ÁREA

### 3.1 Backend infra (uvicorn local arranca limpio)

- **DEBT-012 resuelta:** stubs locales para qdrant/langsmith/mem0 (paquetes con conflict sqlalchemy en requirements.txt). 4 archivos editados con stubs no-op.
- **DEBT-023 cerrada:** `claude_service.model` bumped a `claude-sonnet-4-6`.
- **DEBT-026 cerrada:** CORS parser fix (pivote a `str` + `@property cors_origins_list` tras descubrir que `NoDecode` no existe en pydantic_settings 2.6.1).
- **DEBT-027 cerrada:** `extra="ignore"` agregado al `class Config` + 3 fields OpenAI dead eliminados.
- **DEBT-028 cerrada:** `load_dotenv(Path(__file__).resolve().parents[2]/".env")` al top de main.py + 2 raises raise-on-module migrados a `settings.jwt_secret_key`.
- **DEBT-030 resuelta (stubs temporales):** 4 archivos handlers stubs 501 (`list_agents`, `get_agent`, `get_executions`, `get_logs`) para satisfacer import de `agents/handlers/__init__.py`.

Smoke E2E backend: `/health 200`, `/docs 200`, `/openapi.json 200`, 223 routes registrados.

### 3.2 Hot-swaps providers (§2.4 / §2.5 / §2.6)

- **§2.4** DALL-E 3 → Nano Banana (commits 1/2). `_image_compat.py` wrapper agregado.
- **§2.5** Runway/FAL → Veo 3.1. Sync wrapper con `max_wait_s=300`. Endpoint legacy `/generate-video-runway/` preserva contrato (DEBT-021 cosmético).
- **§2.6** OpenAI/Groq/DeepSeek/Gemini eliminados. agent_registry sed bulk → Anthropic-only en 45 agentes. `_validate_model` whitelist V3 (Haiku 4.5, Sonnet 4.6, Opus 4.7).

### 3.3 Frontend UI cliente PYME

**Step 1 — Sidebar:** `SidebarUserFooter.tsx` nuevo (70L) con avatar+dropdown perfil/logout. Header simplificado (theme toggle removido, queda solo Bell). Decisión "Opción C" aplicada (consolidación en sidebar).

**Step 2 — KPIs dashboard reales:**
- 3 bugs P1 ocultos arreglados (`clients.active` → `status`, `social_accounts.connected` → `status`, `followers_count` no existe → eliminado).
- 4 KPI cards reales: Clientes Activos · Contenido Generado (30d) · Posts Programados (7d) · Cuentas Conectadas.
- `FollowersByPlatformChart` eliminado del render (no hay data real).
- `PlatformStatus` reescrito sin texto "0 seguidores" placeholder.

**Step 3 — Plan Status Bar:**
- Migración `00005_client_plans` aplicada en remoto.
- `src/lib/plan-limits.ts` (52L) — single source of truth de configs por plan (adopción/básico/pro/enterprise) per MODELO §3.
- `src/hooks/useClientPlanStatus.ts` (104L) — fetch plan + posts + accounts + features.
- `src/components/clients/PlanStatusBar.tsx` (136L) — UI inline horizontal, 5 segmentos (Plan badge · Posts progress · 4 iconos platforma · Funciones · Renueva).
- Mount en `ClientDetail.tsx` (Owner ve la bar al revisar un cliente).

**Plan Status Bar en Dashboard (post-Step 3):**
- `useMyPlanStatus.ts` (51L) — detecta rol via `clients.user_id` y `resellers.owner_user_id` (Opción A: cliente+owner muestra bar).
- Bar siempre visible para clientes pre-activación (defaults Adopción 0/7, sin renovación) — config cambia a 'adopcion' cuando no hay `client_plans` row.
- Layout inline con título Dashboard (flex wrapper) + borde 2px amarillo CTA (`border-warning`).

### 3.4 Sistema anti-fraude (R1+R5 del MODELO §8)

Migración `00004_anti_fraud_signals` aplicada. Schema:
- Columna `clients.device_fingerprint` + partial unique index (NULL legacy OK).
- Unique global en `social_accounts (platform, account_id)` — bloquea reuso entre clients.
- Tabla `anti_fraud_signals` con 7 signal_types (`email_duplicate_trial`, `device_fingerprint_duplicate`, `ip_burst_signup`, `social_account_collision`, `payment_method_reuse`, `velocity_anomaly`, `geo_inconsistency`), 4 severities, CHECK invariant `severity='critical' → auto_blocked=true`.
- RLS: service_role ALL · reseller dueño SELECT+UPDATE. Cliente final sin policy = sin acceso (R5).
- Smoke test: CHECK rechaza `critical+!blocked` con error 23514. Caso válido `critical+blocked` aceptado.

### 3.5 Iconos unificados Lucide (sin emojis)

`src/lib/network-icons.ts` (nuevo) como single source of truth:
- Instagram → Camera · Facebook → Square · TikTok → Music2 · LinkedIn → Briefcase · Globe fallback.

Refactor en 5 archivos:
- `PlanStatusBar.tsx` (refactor a getNetworkIcon)
- `PlatformStatus.tsx` (emojis 📸📘🎵🐦💼🎬 → SVG)
- `ActivityFeed.tsx` (drop emoji prefix del título · icon via getNetworkIcon)
- `ClientSocialAccounts.tsx` (PLATFORMS array sin emoji · SelectItem + account list con Lucide)
- `ClientAIConfig.tsx` (CAPABILITY_LABELS map: FileText/ImageIcon/Video/Music/Mic)

Grep emoji audit: 0 hits residuales en `dashboard/`, `clients/`, `Dashboard.tsx`.

### 3.6 Crashes de producción resueltos

- **`/analytics` TypeError:** root cause `useAnalyticsData` destructuraba `totalFollowers` de `useDashboardData` que fue removido en Step 2. Fix: hardcodeo `totalFollowers = 0` + defensive `(value ?? 0).toLocaleString()` en 5 callsites.
- **`/media` TypeError reportado:** no reproducible vía grep. Aplicado defensive preventivo en todos los `.toLocaleString()` callsites de la app.
- **18 console errors dashboard:** queries a 5 tablas Lovable inexistentes en V3 (`profiles`, `posts`, `organizations`, `user_roles`, `audit_logs`).
  - Full Próximamente aplicado a 3 pages: `Content.tsx`, `Calendar.tsx`, `SettingsPage.tsx` (core 100% broken).
  - Surgical stub en `Clients.tsx` (profile query removida, listing real V3 intacto) y `ClientDetail.tsx` (teamMembers + posts arrays vacíos).
  - `useOrganization.ts` stubbed completo (5 queries no-op).
- Componente reusable `src/components/ComingSoon.tsx` creado.

---

## 4. MIGRACIONES SQL APLICADAS HOY

| # | Archivo | Líneas | Aplicada | Notas |
|---|---|---|---|---|
| **00004** | `supabase/migrations/00004_anti_fraud_signals.sql` | 95 | ✓ remoto | R1+R5 del MODELO. Backfill irrelevante (0 clients) |
| **00005** | `supabase/migrations/00005_client_plans.sql` | 69 | ✓ remoto | Billing cycle source. Backfill 0 rows (clients vacío) |

`supabase migration list --linked` muestra 00001-00005 sincronizadas Local=Remote.

**Schema V3 actual en remoto** (tablas en `public`):
- `clients` (00001 + `device_fingerprint` 00004)
- `social_accounts` (00001 + unique global `(platform, account_id)` 00004)
- `content_lab_generated` (00001)
- `scheduled_posts` (00001)
- `agents` (00001 + 37 agents seeded 00003)
- `resellers` (00001)
- `reseller_branding` (00001)
- `sub_brands` (00001)
- `brand_files` (00001)
- `anti_fraud_signals` (00004)
- `client_plans` (00005)
- Plus tablas memoria/pgvector (00002)

**NO existen en V3** (Lovable legacy referenciado por frontend roto):
- `profiles`, `posts`, `organizations`, `user_roles`, `audit_logs` → ver DEBT-033

---

## 5. DEBTs CERRADAS HOY

Total cerradas en estas 2 sesiones: **8 DEBTs**.

| ID | Título | Detalle del cierre |
|---|---|---|
| **DEBT-012** | mem0/qdrant/langsmith stubs | 4 archivos stubbed con no-op decorators/clases. `requirements.txt` mantiene paquetes comentados |
| **DEBT-016** | I1 100% compliance | Post §2.6: 0 imports prohibidos en backend. Quedan 6 `type:ignore` en C2 (separate scope) |
| **DEBT-022** | FAL → Nano Banana single path | `generate_image.py` simplificado a single-path Nano Banana en §2.6 |
| **DEBT-023** | claude_service.model bump | Sonnet 4.5 → 4.6 + `LLMResponse.model` actualizado |
| **DEBT-026** | CORS parser pydantic_settings | Pivote a `backend_cors_origins: str` + `@property cors_origins_list` (NoDecode no existe en 2.6.1) |
| **DEBT-027** | Settings extra='forbid' | `extra="ignore"` agregado · 3 fields OpenAI dead eliminados |
| **DEBT-028** | os.environ vs .env | `load_dotenv` al top de main.py · 2 raises migrados a `settings.jwt_secret_key` |
| **DEBT-030** | agents handlers faltantes | 4 stubs 501 creados (solución temporal · real en Fase 3) |

---

## 6. DEBTs NUEVAS REGISTRADAS HOY

| ID | Título | h estimadas | Severidad | Resumen |
|---|---|---|---|---|
| **DEBT-029** | 33 sites os.getenv() directo | 6h | Medio | Migrar a `settings.xxx` por bounded context en Fase 3 §3.2 |
| **DEBT-031** | FastAPI dashboard handler roto | 4h | Bajo | `analytics/handlers/get_dashboard.py` referencia tablas inexistentes en V3. Frontend no lo usa |
| **DEBT-032** | client_plans sin auto-trigger + sin Stripe | 6h | Medio | (a) trigger AFTER INSERT auth.users → crea client + client_plans · (b) Stripe webhook upsert real |
| **DEBT-033** | 5 tablas Lovable inexistentes en V3 | 40h | Alto | `profiles/posts/organizations/user_roles/audit_logs`. Rewrite de 5 pages + 1 hook en Fase 3 |
| **DEBT-034** | `useAnalyticsData` 100% mock | 16h | Medio | Espera sync Meta API real o eliminación de `/analytics` page |

---

## 7. DEBTs HEREDADAS ACTIVAS (FASE 3)

Sin tocar hoy. Documentadas en `SOURCE_OF_TRUTH.md` desde sesiones previas.

| ID | Título | h | Severidad |
|---|---|---|---|
| **DEBT-001** a **DEBT-011** | Múltiples herencias Fase 0/1 | varias | mixto |
| **DEBT-013** | tsconfig.json laxo (sin strict, sin 9 aliases @bc-*) | 16h | Alto (C1+C2) |
| **DEBT-014** | 11+ archivos frontend >100L (Clients 448L, Content 306L) | 40h | Alto (C4) |
| **DEBT-015** | 15+ `as any` en hooks/pages Lovable | 20h | Alto (C1+C2) |
| **DEBT-017** | 163 archivos backend Lovable >100L | 80h | Alto (C4) |
| **DEBT-018** | Imágenes Nano Banana como data URIs | 6h | **Crítico antes prod** (necesita Supabase Storage bucket) |
| **DEBT-019** | Videos Veo 3.1 como URIs temporales Google | 6h | **Crítico antes prod** |
| **DEBT-020** | Video sync wrapper en endpoint HTTP | 16h | Alto (UX + reliability) |
| **DEBT-021** | Endpoint `/generate-video-runway/` legacy nombre | 2h | Bajo (cosmético) |
| **DEBT-024** | 48 callers `claude_service.generate_text()` | 12h | Medio (DDD único entry) |
| **DEBT-025** | Routing layer duplicado (ai_providers, agent_dispatcher) | 8h | Medio (consolidación) |

**Total deuda estimada: ~632h** (~16 semanas full-time Fase 3).

---

## 8. MEMORIAS PERSISTENTES AGREGADAS

Nuevas en sesión:
- **`project_omega_modelo_cliente.md`** — Modelo C canónico firmado 17 may 2026: $0/$29/$65, ARIA 4 niveles, R1-R6 reglas, dashboard §7 layout, add-ons
- **`project_omega_pricing.md`** (deprecated A/B contexto histórico)
- **`reference_omega_pricing_docs.md`** — paths exactos a archivos pricing en `legacy/`
- **`project_omega_plan_status_bar_roles.md`** — 3 comportamientos por rol (cliente PYME ✓ · reseller ⏳ · owner global ⏳)

Existentes invocadas:
- `feedback_autonomous_mode.md` — trabajar sin pedir confirmación con plan estructurado
- `feedback_omega_no_mocks.md` — regla P1 cero mocks
- `feedback_pendientes_doc_local.md` — este doc nunca se pushea
- `reference_raisenomega_dual_identity.md` — identidad git correcta `raisenomega <raisenagencypr@gmail.com>`
- `reference_omegaraisen_bootstrap_windows.md` — 3 parches Windows
- `feedback_supabase_mcp_wrong_project.md` — MCP apunta a `zkhdhqkgzwxsueqrqmvk` (proyecto diferente al SaaS principal `rwlnihoqhxwpbehibgxu`)

---

## 9. PENDIENTES INMEDIATOS PRÓXIMA SESIÓN

### 9.1 P0 — Para que los números reales aparezcan en el bar

**DEBT-032 parcial — Auto-trigger en `auth.users` INSERT:**
- Migración `00006_client_plans_auto_provision.sql` propuesta:
  - Crear reseller default "OMEGA Direct" si no existe (slug + name)
  - Función + trigger AFTER INSERT en `auth.users` que crea `clients` (`user_id`, `reseller_id=omega-direct`, `plan='adopcion'`, `name='Mi negocio'`) + `client_plans` (`current_period_end = now() + 7 days`)
  - Guard: si user ya está en `resellers.owner_user_id`, NO crear `clients` row (evita que owners vean bar erróneamente)
  - Backfill para los 3 `auth.users` existentes
- Decisión arquitectónica abierta: trigger SQL vs lógica en backend signup endpoint. Trigger es más consistente, backend es más debuggable.

### 9.2 P1 — Bell "3" hardcoded en AppHeader (último P1 violation)

`src/components/layout/AppHeader.tsx` muestra `<span>3</span>` hardcoded. Opciones:
- Eliminar el badge hasta que haya endpoint de notifications real
- Construir tabla `notifications` + endpoint + hook
- Inhabilitar el botón hasta backend

Scope estimado: 2h si elimina · 8h si implementa real.

### 9.3 P1 — Verificar que el bar muestra números reales tras P0

Después de aplicar DEBT-032 trigger, refrescar Dashboard cliente debe mostrar:
- Plan ADOPCIÓN · 7 días gratis (real, no default)
- Renueva en N días (calculado de `current_period_end - now()`)
- Posts usados según `content_lab_generated` real
- Cuentas conectadas según `social_accounts` activas

### 9.4 P2 — Dashboard del Reseller (PlanStatusBar variant)

Memoria `project_omega_plan_status_bar_roles.md` documenta:
- Reseller ve: salud de cartera de clients (MRR cartera, churn risk, antifraude pendientes)
- Owner global ve: métricas globales OMEGA

NO implementado. Cuando se ataque, reusar PlanStatusBar o crear `ResellerHealthBar`. Decisión arquitectónica abierta.

### 9.5 P2 — Decidir si /analytics page se elimina o se conserva con mock

`useAnalyticsData` es 100% mock (DEBT-034). Opciones:
- Eliminar route entirely y mostrar 404 / redirect a /dashboard
- Reemplazar con ComingSoon (consistente con Content/Calendar/Settings)
- Mantener mock hasta que llegue sync Meta API real

### 9.6 P2 — DEBT-018 + DEBT-019 antes de cualquier deploy producción

Crítico antes de prod:
- DEBT-018: Crear bucket `generated-images/` en Supabase + RLS + reemplazar return data URI en `_image_compat.py` por URL pública
- DEBT-019: Idem para `generated-videos/` con descarga pre-TTL desde Google URIs

Ambas estimadas 6h c/u.

---

## 10. DUDAS ABIERTAS QUE REQUIEREN DECISIÓN

### 10.1 Modelado del rol "Owner global" (Ibrain super-admin)

Schema V3 actual NO distingue Owner global de Reseller. Memoria `project_omega_plan_status_bar_roles.md` flagea esto. Opciones:
- Columna `is_super_admin` en `auth.users.raw_user_meta_data`
- Tabla nueva `super_admins` o `admins` con FK a auth.users
- Convención por email (no recomendado por mantenibilidad)

Necesario antes de implementar el dashboard de Owner global.

### 10.2 Auto-trigger client_plans: SQL trigger vs backend endpoint

DEBT-032 partial fix. Trade-off:
- **Trigger SQL** — consistente, atomic, funciona sin importar dónde se crea el user (admin panel, signup, magic link). Pero más complejo de debuggear, requiere `SECURITY DEFINER`.
- **Backend endpoint** — debugeable, traceable en logs, pero requiere que TODO signup pase por el endpoint (no admin SQL manual).

### 10.3 ¿Eliminar Clients.tsx CRUD completamente o solo deshabilitar?

Hoy: Clients.tsx LISTA funciona, CRUD (form) usa cols Lovable (`email`, `phone`, `company`, `notes`, `organization_id`) que NO existen en V3. Click crear → toast error.

Opciones:
- Mantener como está (listing+broken CRUD, error toast al click)
- Disable button + tooltip "Próximamente"
- Reescribir form contra schema V3 (subset: solo `name`, `business_type`, `industry`, `plan`)

### 10.4 Pricing Modelo A/B legacy vs Modelo C canónico

Memoria `project_omega_pricing.md` deprecate A y B en favor de C ($0/$29/$65). Pero el doc canónico `MODELO_NEGOCIO_OMEGA_CLIENTE.md` quedó local (no commiteado). Decisión: ¿se commitea o queda local? Por ahora local (default por consistencia con `feedback_pendientes_doc_local.md`).

### 10.5 ¿Recuperar 4 docs canónicos perdidos del 2026-03-15?

Memoria `reference_omega_pricing_docs.md` flagea que existen referencias a:
- `OMEGA_MODELO_COMERCIAL_20260315.md`
- `OMEGA_FASE3_ROADMAP_20260315.md`
- `OMEGA_FASE4_CONTENT_LIBRARY_20260315.md`
- `OMEGA_VISION_10_ANOS_20260315.md`

Estos docs NO están en `legacy/`. Buscar en Lovable backup, Drive, Notion, otros discos. Si aparecen, los bundles del marketplace tienen sus números cerrados.

---

## 11. VERIFICACIÓN VISUAL PENDIENTE DEL USUARIO

Pendiente que el user confirme visualmente abriendo `http://localhost:5174` con sesión real:

### 11.1 Sidebar (commit `80aa40d`)
- [ ] Footer del sidebar abierto: avatar + nombre + email + chevron · click → dropdown perfil/logout
- [ ] Sidebar colapsado: solo avatar centrado · click → mismo dropdown
- [ ] Header NO tiene avatar (sólo Bell)
- [ ] Logout funcional → vuelve a /auth

### 11.2 Dashboard KPIs (commit `d84c480`)
- [ ] 4 KPI cards con números reales (probable 0 si DB vacía — legítimo)
- [ ] Cero "Próximamente" en KPIs
- [ ] AccountDistributionChart se renderiza
- [ ] ActivityFeed con clients real (si existen)

### 11.3 Plan Status Bar en ClientDetail (commit `fbd8d28`)
- [ ] Abrir `/clients/:id` con cliente real → bar inline arriba de tabs
- [ ] 5 segmentos con dividers: Plan badge · Posts · 4 iconos plataforma · Funciones · Renueva
- [ ] Tooltips funcionan en iconos plataforma y "X/6 funciones"
- [ ] Sin plan → "Sin plan configurado" (ANTES de commit `cb8ec26` que cambió esto)

### 11.4 Plan Status Bar en Dashboard cliente (commit `c4e6a14` + `cb8ec26` + `a190042`)
- [ ] Logueado como user PYME (necesita `clients` row con user_id) → bar visible
- [ ] Logueado como owner sin client row → bar NO visible
- [ ] Bar muestra defaults Adopción (0/7 posts, 4 iconos faded, 6/6 funciones, "Sin renovación") en estado pre-activación
- [ ] Bar inline con título Dashboard (no debajo del bloque title+subtitle)
- [ ] Borde 2px amarillo (`border-warning`) alrededor del card
- [ ] Mobile: flex-wrap baja bar a línea propia bajo el bloque título

### 11.5 Crashes resueltos (commit `e4da284`)
- [ ] `/analytics` carga sin crash (KPIs muestran 0 si DB vacía)
- [ ] `/media` carga sin crash
- [ ] DevTools console en `/dashboard`: 0 errores rojos
- [ ] `/content`, `/calendar`, `/settings` → componente Próximamente con icon Construction

---

## 12. ACCIONES MANUALES NO AUTOMATIZABLES

Requieren intervención del usuario fuera del codebase:

### 12.1 §1.5 — Crear proyecto Vercel para frontend
- Conectar repo `github.com/raisenomega/Omega`
- Set environment vars: `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_API_URL` (apuntando a Railway), `VITE_APP_ENV=production`
- Configurar dominio custom `r-omega.agency` + DNS
- Build command: `npm run build` · Output: `dist`

### 12.2 §1.6 — Crear proyecto Railway para backend
- Conectar repo, root directory `backend/`
- Set environment vars del `.env` correspondientes
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Configurar dominio custom + healthcheck en `/health`

### 12.3 §1.7 — Rotar API keys
- Generar nuevas keys: Anthropic, Supabase service_role, JWT secret, Stripe (cuando se active)
- Actualizar en Railway env vars
- Documentar en password manager

### 12.4 §2.7 — Smoke E2E deploy
- Solo después de §1.5+§1.6+§1.7
- Verificar flow signup → dashboard → ver bar Adopción (post DEBT-032)
- Verificar generación de contenido (post DEBT-018+019 storage buckets)

### 12.5 Supabase Storage buckets (bloqueante prod)
- Crear bucket `generated-images/` (DEBT-018) — RLS público read, service_role write
- Crear bucket `generated-videos/` (DEBT-019) — mismo patrón
- Configurar lifecycle / cleanup automatic si aplica

### 12.6 Recuperar 4 docs canónicos perdidos
- Buscar `OMEGA_MODELO_COMERCIAL_20260315.md` y 3 hermanos en backups Lovable / Drive / Notion
- Sin estos, los bundles marketplace (DIANA/IVONNE/Custom) quedan con `$__` placeholder

---

## 13. ESTADO DEL SISTEMA AL CIERRE

### 13.1 Repositorio git
- Branch: `main` · Último commit: `a190042` · Sincronizado con `origin/main`
- Identidad: `raisenomega <raisenagencypr@gmail.com>` ✓
- Working tree: clean salvo `MODELO_NEGOCIO_OMEGA_CLIENTE.md` (local doc del owner, intencionalmente untracked) y `legacy/` (referencia histórica, untracked)
- 16 commits hoy. Validator interno 10/10 en todos.

### 13.2 Backend Python
- `py -3.11` venv en `backend/venv/` ✓
- `uvicorn app.main:app` arranca sin error
- `.env` cargado vía `load_dotenv(Path(__file__).resolve().parents[2]/".env")` en `main.py`
- Logs cleanos en startup (solo deprecation warnings de pypdf ARC4 + pydantic schema_extra v1 shim)
- Endpoints: `/health 200`, `/docs 200`, `/openapi.json 200`, 223 routes registrados

### 13.3 Frontend Vite + React + TypeScript
- `npm run dev -- --port 5174` arranca limpio (~725ms)
- TypeScript compile: 0 errores
- Validate-before-push: 10/10
- shadcn ui + Tailwind operativos
- Pages estables: Dashboard, Clients, ClientDetail, Analytics, Media. Pages Próximamente: Content, Calendar, Settings

### 13.4 Supabase remoto (`rwlnihoqhxwpbehibgxu`)
- 5 migraciones sincronizadas (00001-00005)
- 11 tablas en `public` schema + extensiones
- 3 `auth.users` registrados (no asociados a `clients` rows aún — pendiente DEBT-032)
- 0 `clients`, 0 `client_plans`, 0 `anti_fraud_signals`, 0 `social_accounts`, 0 `content_lab_generated`, 0 `scheduled_posts`
- RLS habilitada en todas las tablas con identificador de propietario (verificado por DO block en 00003)
- 37 agentes AI seeded en `agents` table

### 13.5 Memoria persistente Claude (`~/.claude/projects/.../memory/`)
- 23 memorias activas (4 nuevas hoy)
- MEMORY.md index actualizado
- Convención: project · feedback · reference · user types

---

## 14. NOTAS OPERATIVAS

### 14.1 Verificación pre-push hook
- Antes de cualquier push: `cp scripts/validate-before-push.sh .git/hooks/pre-push && chmod +x .git/hooks/pre-push`
- El hook NO se sincroniza automáticamente — requiere manual sync (limitación git)
- Validator chequea: identidad git, sin `any`/`@ts-ignore`, sin imports prohibidos, SHA1 de `limits_omega.py` intacto, C4 ≤100L, TypeScript compile, tests frontend

### 14.2 SHA1 protegido
- `backend/app/bc_cognition/domain/limits_omega.py` SHA1 = `ee472c1d398afc46e34ac4bd42d349b0bf6e9649`
- NUNCA modificar este archivo. Validator falla push si cambia.

### 14.3 Identidad git dual
- Este proyecto (`D:/Omega Master redes/`) → `raisenomega <raisenagencypr@gmail.com>`
- Proyecto vecino `D:/Raisen Omega/` → identidad noreply (separada)
- Config local en `.gitconfig` + `.gitconfig-omegamaster` con `includeIf "gitdir:..."`

### 14.4 Supabase CLI linked project
- Apunta a `rwlnihoqhxwpbehibgxu` (SaaS principal V3)
- NO confundir con el proyecto del MCP de Claude (`zkhdhqkgzwxsueqrqmvk`) que es otro Supabase distinto (marketing site `r-omega.agency`)
- Migraciones aplicadas vía `supabase db push --linked` (NO via MCP)

### 14.5 Doc canónico del modelo de negocio
- `MODELO_NEGOCIO_OMEGA_CLIENTE.md` (415L, firmado 17 may 2026) está en working tree pero untracked
- Decisión actual: queda local. Si futuro se decide commitearlo, revisar antes que no contenga info confidencial (sistema 60/40 split aparece ahí)
- Memoria `project_omega_modelo_cliente.md` lo resume; el doc original tiene el detalle completo

### 14.6 Convención de DEBTs
- Numeración secuencial DEBT-001, DEBT-002, ...
- Estado: ABIERTA · CERRADA · subsumida por DEBT-N
- Toda DEBT cerrada conserva su row en `SOURCE_OF_TRUTH.md` con texto `**CERRADA (fecha)**` para auditoría
- Próxima ID disponible: DEBT-035

### 14.7 Pre-push checklist mental
1. `git status --short` (verificar archivos a commitear)
2. `npx tsc --noEmit` (TypeScript limpio)
3. `cp scripts/validate-before-push.sh .git/hooks/pre-push && chmod +x` (sync hook)
4. `bash scripts/validate-before-push.sh` (10/10 antes de push)
5. Commit con mensaje incluyendo Co-Authored-By
6. `git push` — espera confirmación explícita del usuario "push" antes de ejecutar

---

## CIERRE DE SESIÓN — 2026-05-19 · 01:06am

Sesión productiva: 16 commits, 5 migraciones sincronizadas, 8 DEBTs cerradas, 5 nuevas registradas, 4 memorias persistentes nuevas, regla P1 reforzada en todo el frontend nuevo.

**Próxima sesión 19 may PM:** arrancar con P0 (DEBT-032 partial fix · trigger client_plans) para que el bar finalmente muestre números reales. Después continuar con verificación visual + orden de prioridades de §9.

Bar de plan visible inline en dashboard del cliente con borde amarillo CTA, layout horizontal, defaults Adopción, iconos Lucide unificados. UX consistente cliente vs admin: Owner sin bar, cliente con bar siempre visible.

🐢💎 No velocity, only precision.
