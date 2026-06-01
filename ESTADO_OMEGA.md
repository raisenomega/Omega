# ESTADO OMEGA · Documento Vivo · Última actualización: 1 jun 2026 (HEAD `cb585b6` · Switcher V1 CERRADO 100% + reconciliación censo · 4 deudas técnicas migradas a SOT §6 · regla de cierre de sesión añadida §7) · 29 may 2026 (Sprint 7 · DEBT-097 CERRADA · Modo Supervisado acotado: máquina estados P2/P3 + panel cola por-negocio + toggle · cron auto → DEBT-096 · DEBT-102 CERRADA widget "Qué aprendió ARIA" · cross-client → DEBT-033 · sync MCP v2.0 Zernio · DEBT-MCP-ZERNIO/ANALYTICS + 3 HERMES registradas · orden Sprint 8 re-locked) · 28 may 2026 (sesión 6 · DEBT-099+v2 CERRADAS · plan bar 7 estados · modelo reseller LOCKED · E2E prod ✅)

> **Fuente de verdad OPERACIONAL** (qué está hecho, qué falta, en qué orden).
> Fuente de verdad TÉCNICA (contratos DDD, arquitectura, detalle de DEBTs): `SOURCE_OF_TRUTH.md`.
> Este doc reemplaza los 8 `PENDIENTES_Y_PROGRESOS_*.md` (consolidados · detalle granular en git history).

---

## 1 · SISTEMA AHORA

| Componente | Estado | Identificador |
|---|---|---|
| Git HEAD | ✅ | `cb585b6` (1 jun · post-Switcher V1 + reconciliación censo · correr `git log --oneline -1` para el vivo) |
| Frontend | ✅ Vercel | `omegaraisen.agency` (deploy auto en push a `main`) |
| Backend | ✅ Railway | `omega-production-3c67.up.railway.app` |
| Supabase | ✅ | proyecto `rwlnihoqhxwpbehibgxu` (PostgreSQL + RLS) · **Site URL = `https://omegaraisen.agency`** (corregido 28 may) · Redirect URLs `omegaraisen.agency` + `omegaraisen.agency/**` |
| Migraciones | ✅ | `00001` → `00042` aplicadas (28 may · +`00041` signup trigger idempotente `6bab6a0` · +`00042` `clients.user_id` ON DELETE CASCADE `2960000` · ver `SOURCE_OF_TRUTH.md §16`+§18) |
| Crons APScheduler | ✅ | **15/15** (en `backend/app/main.py` · incluye `reset_credit_periods` 00:05 fin-de-mes DEBT-052 · `decision_evaluator` DEBT-100 · `strategy_generator` DEBT-096 F2 · lista completa en `DDD_REGLAS_OMEGA.md` X3) |
| Alertas Email (SENTINEL) | ✅ **prod confirmado 28 may 07:00** | Resend live · **alarma** (`alert_dispatcher` · score<80 · siempre · E2E 25 may) + **brief al owner** (`brief_dispatcher` · DEBT-105 `bae2b3d`): SENTINEL diario condicional (issues>0/score<85 · score 86/100 reportado 28 may) · ORACLE semanal siempre · best-effort · `RESEND_API_KEY` puesta |
| Alertas Telegram | ⏸️ | Preparado · activa al pegar `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` (falta crear el bot) |
| Email template `confirm_signup` | ✅ (28 may) | `supabase/email_templates/confirm_signup.html` `ff73922` · paleta OMEGA gold `#EEA62B` + Syne `RAISEN. OMEGA` · cargado al Supabase Dashboard manualmente (Supabase no expone API templates) |
| Login → /dashboard global todos los roles | ✅ (28 may · commit histórico `12dfed8`) | wizard inicial eliminado del repo · `App.tsx` sin ruta `/onboarding` · `ProtectedRoute.tsx` sin redirect · 4 roles probados E2E prod ~07:33 AM (super_owner · reseller · cliente PYME · cliente nuevo fresh) |
| Self-service signup E2E producción | ✅ (28 may ~07:33 AM) | signup → email OMEGA → confirm → `/dashboard` → nudge "Agregá tu primer cliente" en Card Notificaciones → click → `/clients` → wizard opcional → cliente real guardado → nudge auto-oculto |
| Plan status bar · 7 estados legibles | ✅ (28 may) | `55cc797` · trial >3d ámbar · trial ≤3d rojo · trial vencido rojo+CTA · plan ≤30d urgencia · plan 31-365d fecha corta es-AR · plan venció rojo · **perpetuo (>365d) oculto** (fix `Renueva 26880d`) · upgrade tier completo (ADOPCION→/settings · BÁSICO→PRO · PRO→Enterprise · ENTERPRISE sin CTA) |

### Acciones owner pendientes (Railway env vars)
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` → activa Telegram (sin code deploy · el restart re-lee settings).
- `ALERT_EMAIL_FROM` (opcional) → cambiar de `onboarding@resend.dev` a un dominio verificado en Resend cuando lo tengas.
- **OAuth (desbloquea DEBT-040 publicación real):** `META_APP_ID`+`META_APP_SECRET` · `GOOGLE_CLIENT_ID`+`GOOGLE_CLIENT_SECRET` · `OAUTH_ENCRYPTION_KEY` (`Fernet.generate_key()`) · `OAUTH_REDIRECT_BASE`.
- **Stripe:** registrar el webhook en el dashboard + crear los productos/prices faltantes → activa checkout créditos/agentes/ARIA/Enterprise (hoy 503 honesto). Pasar a LIVE mode cuando esté listo.

### Cuentas test owner (enterprise perpetuo · acceso total sin paywall · 28 may)
- **`cliente@omega.com`** · client `Zafacones Ramos` (`afb9f578-...`) · DB: `clients.plan='enterprise'` + `client_plans.plan='enterprise'` + addons `[video_pack_cinematic_pro, brand_dna_premium, aria_pro]` + `current_period_end=2099-12-31` + `client_agent_credits.budget=$99,999.99/mes` periodo `2099-12-31`. FE: `useDemoMode` default ahora `'enterprise'` (antes `'basic'`); toggle muestra Enterprise/PRO/Básico para testing UX.
- **`reseller@omega.com`** · `resellers.plan='enterprise'` (era 'pro')
- **Owner Ibrain** (`OMEGA Direct` · user `741ace1c-...`) · `plan='enterprise'` + `is_super_owner=True` desde antes — no necesita demo mode.
- **Política**: estas 3 cuentas NUNCA deben ver paywall ni restricción de plan. Si aparece un nuevo gate, agregar bypass para los emails de arriba o reverter a defaults menos restrictivos.

---

## 2 · DEBTs CERRADAS · ~50 total

> Detalle completo + hashes históricos: `SOURCE_OF_TRUTH.md §6` + `git log`. Resumen por sprint:

- **Sprint 1 (21 may):** Brand DNA Builder · ARIA memory · `prompt_vault`.
- **Sprint 2 (22 may):** persistencia Brand DNA (00017) · Virality Score · A/B variaciones · DEBT-018/019/020/044 · seguridad GUARDIAN 4B (00022).
- **Sprint 3 (23-24 may):** Content Lab completo (texto/imagen/video) · 20 DEBT-CL (003→022) · DEBT-VID-001 · DEBT-037 (ARIA Premium client) · DEBT-CL-017/018/020.
- **Sprint 4A (25 may):** SENTINEL subagent + builders · `input_sanitizer` · DEBT-002 analytics honesto · config fail-secure.
- **Sesión 25 may (día):** DEBT-031 (calendar legacy) · AUDIT 1/2 wizard% + picker · BUG A persistencia · wizard 3 fixes · 🔒 role server-side (`33166e4`) · hard-delete cliente · logo overlay Fase 1 · ARIA contexto ampliado.
- **Sesión 25 may (noche):** ARIA history DESC+reversed (`3a85fe1`) · ARIA deadlock input (`cece228`) · KPI Posts Programados (`44ca9d5`) · TAREA 2 popup 3 botones + 00025 `published_manual` · FIX P1 update_status (`84a05fe`) · FIX P5 conteos (`b2ab2fe`) · get_stats verde (`f807f2c`) · ISSUE 1 FK al agendar 409 (`59d182a`+`c9bfdb0`) · **outcome_evaluator 4A-2** (`5a834ed`+`3490ce0`+`8016531` · 00026) · **SENTINEL 8 endpoints superadmin** (`14b5d37`) · **alert_dispatcher** (`062353b`) · fix tablas fantasma sentinel (`91ad252`) · test regresión auth role (`f4c01b2`) · **DEBT-054 Info Tab → client_context** (`0946be5`) · consolidación docs → ESTADO_OMEGA único (`5858b12`+`92caa52`+`e8bdfcb`) · **Agente Publicador add-on** (`fd980ff`) · **DEBT-057+058 Tab AI → panel honesto Anthropic-only** (I1 · elimina multi-proveedor legacy + tablas fantasma) · **DEBT-059 logo wizard persiste** (`useUploadBrandLogo` · sube logo_files → `client_brand_assets.logo_file_id` · cierra overlay = Logo Fase 2 · P1) · **DEBT-061 crisis_manager guardrail P4** (`_assert_human_in_the_loop` enforza ACCIONES_PROHIBIDAS · `AUTONOMOUS_PUBLISH_ALLOWED=False` · model vía routing_table I2 · test G2 6/6) · **DEBT-066 + DEBT-072 + DEBT-073** familia "col inexistente" en clientes: header ClientDetail + tarjetas lista + buscador → cols reales (`business_email`/`website`/`industry`) · dot "activo" → `status === "active"` (antes `client.active` inexistente) · **DEBT-063** ARIA level real del backend (`max(plan, aria_level)`) → cliente que pagó Premium no ve "Actualizar" · **DEBT-062** social_accounts INSERT/render → cols reales (`approx_followers`/`status`) · CRUD "Agregar cuenta" destrabado · **DEBT-065** Tab Agente rediseñado a nivel ARIA del cliente + estado (`aria-levels.ts` compartido · sin legacy assigned_to) · **DEBT-042** regiones como chips con labels legibles en Info Tab (`REGION_LABELS` · `InfoRow.chips`) · **DEBT-068** uploads de imagen/video async vía `asyncio.to_thread` (+ overlay/find_logo · event loop no bloquea · P0 de escala) · **DEBT-069** timeout Nano Banana 90s (`asyncio.wait_for` → `ImageError("timeout")`) · **DEBT-070** rate-limit real (`RateLimitMiddleware` in-memory por IP · cablea `rate_limit_per_minute` · 429+Retry-After · antes config muerta) · **DEBT-071** retry+backoff de transitorios (429/5xx) en generación de imagen · 429 de Google → HTTP 429+Retry-After (antes 503 opaco).
- **Sesión 27 may (marathon · ~40 commits · `c2f26c7`→`5a9856b`):** **DEBT-052 créditos prepagados END-TO-END** FASE 4 (checkout 4 packs Micro$9/Starter$25/Plus$59/Ultra$119 + enrolamiento + cron fin-de-mes 12º job + superadmin mover/liberar + auto-recarga toggle) + FASE 5 widget AI Tab (`c2f26c7`→`d0c1922`·`67d1618`) · **DEBT-091** checkout Agent Add-Ons Rex/Rafa/Maya Stripe real (`46a88e6`) · **DEBT-048** ARIA attention memory + Voyage AI I1#3 (00036·`625f089`) · **DEBT-047** persistent jobstore deploy-safe (`31d0062`) · **DEBT-038** Stripe Customer Portal (`067529f`) · **DEBT-060** media bucket folder-scoped (00035·`d83e0d1`) · **DEBT-075** SSRF host guard (`9e5c637`) · **DEBT-085/086** marca→ARIA + confirmación logo (`80db419`) · **DEBT-095** trigger+backfill client_plans (00038/00039·`d5a48b6`+`c583531`) · **OAuth skeleton** Meta+Google (00037·`d9dac19`) · **RONDA E** Centro Inteligencia Fase 2 + auto-publicación esqueleto (`0e1c073`) · **LIMPIEZA** 34 archivos legacy gpt-4/openai/Tavily · **UI/UX**: sidebar colapsable + Add-Ons hub barra-top + hover glossy amber + Tab Agente 2-col + scrollbar oculta + demo→Stripe real · **Seguridad**: password DB rotada + DATABASE_URL actualizada. Migraciones a prod hasta **00039** · Stripe 16 productos + 11 `STRIPE_PRICE_*` + `VOYAGE_API_KEY`.

---

## 3 · DEBTs ABIERTAS · ~1,127h (consolidado owner · 27 may sesión 2 · ver SOT §6 Total + §17 roadmap)

> **Audit cliente E2E (25 may):** +10 DEBTs nuevas (057-066) · **DEBT-057/058/059/061 ya CERRADAS** (Tab AI Anthropic-only · logo wizard · crisis P4 · ver §2). % real cliente: core ~83% · superficie completa ~68%.
> **Audit rendimiento imagen (26 may):** +4 DEBTs (068-071) · **TODAS CERRADAS** (uploads async · timeout Nano Banana · rate-limit cableado · retry+backoff · ver §2). La generación de imagen ya no bloquea el event loop, no cuelga, está rate-limitada y reintenta transitorios.
> **Sesión 27 may (marathon):** cerradas DEBT-052/091/048/047/038/060/075/085/086/095 (–51.5h) · DEBT-040 OAuth con SKELETON + RONDA E en progreso · DEBT-088/092/093/094 + 089/090 registradas (Sprint 7-8). Ver §2.
> **Sesión 27 may (sesión 2 · learning loop + estrategias/modos + FFmpeg + editor):** **DEBT-100 CERRADA** (`866a9d3` · Loop 1 was_correct · hallazgo P1 source_event_id documentado en SOT §6). Registradas DEBT-099/101/102/103/104/105 + FFMPEG-001..004 + EDITOR-001 + OMNI-001 (+ DEBT-096/097/098 ya en SOT §6). Total consolidado ~1,127h. Docs: `ARIA_LEARNING_LOOP_OMEGA.md` + `GEMINI_FFMPEG_OMEGA.md`. Ver tabla 🆕 abajo + SOT §17.

> **Sesión 27 may (sesión 3 · DEBT-105 email brief):** **DEBT-105 CERRADA** (`bae2b3d`) · brief al owner por email: `brief_dispatcher`+`_brief_formatters` (bc_cognition/application · aislados de `alert_dispatcher` por decisión del owner) · SENTINEL diario condicional (issues>0/score<85) + ORACLE semanal siempre · best-effort · test 4/4 · gate 10/10. **Security Dev panel ✅ desplegado** (migr 00040 + tabs SENTINEL/GUARDIAN reales + sidebar · `f0bc79c`/`d666bb4`) · subpartes A-D (Claude DEV chat/terminal) siguen abiertas (DEBT-106 · Sprint 8). **Sprint 7 restante:** DEBT-FFMPEG-001/002/003/004 (6.5h) · DEBT-096/097/099/101/102.

> **Sesión 27 may (sesión 4 · gate hardening + DEBT-FFMPEG):** **gate self-contained** vía 3 fixes (`bfa60c9` ROOT_DIR · `a6143f0` backend/conftest.py · `6c8a21a` CHECK 9 venv directo) → 10/10 desde shell limpio sin env/PATH. **DEBT-FFMPEG-001/002/003/004 CERRADAS** (`c9baba4`) logo overlay end-to-end imagen+video · `nixpacks.toml` con ffmpeg (001) · `_logo_overlay_video.py` FFmpeg subprocess 15%/80%/inf-derecha/20px best-effort (002, scope acotado a overlay) · `_video_compat` aplica tras download (003) · `logo_url` en metadata jsonb sin tabla nueva (004) · ratio imagen Pillow 10%→15% (alineado) · `apply_logo` cableado e2e: ContentLabFormV2 checkbox imagen+video · `useVideoJobPolling` payload · `GenerateVideoRequest` · handler + worker · 11 archivos · test 5/5 · gate 10/10.

> **Sesión 28 may (sesión 5 · DEBT-101 + parches):** **DEBT-101 CERRADA** (`ef00fd0`) ARIA Learning Report semanal · cron lunes 07:05 UTC · 4 archivos nuevos + extensión mínima `brief_dispatcher` (`dispatch_aria_learning_brief` 6L · mismo patrón que sentinel/oracle) · suite 144/144 (+5 nuevos). Bucket `brand-files` privado fix (`967f1a7`): `download_logo_bytes` via service-role en `_logo_overlay` resolvió "logo no persiste" (en realidad: 404 silencioso). Test-accounts enterprise perpetuo (`967f1a7` · cliente@omega + reseller@omega) + `useDemoMode` default `'enterprise'`. Wizard sección 9 (`68b7193`): thumbnail del logo previo con signed URL. **DEBT-IMAGE-ASYNC NUEVA** (`f5d44a1` · 🟠 10h Sprint 8) + timeout Nano Banana 120→180s parche temporal. **Sprint 7 cerradas acumulado**: DEBT-105 + DEBT-FFMPEG-001/002/003/004 + DEBT-101 (≈16.5h netas). **Sprint 7 abierto**: DEBT-099 (🔴 self-service 20h · próxima recomendada) · DEBT-097 (20h) · DEBT-096 (30h) · DEBT-102 (10h) · DEBT-033 (40h scope nuevo).

> **Sesión 28 may (sesión 6 · DEBT-099 self-service E2E + 099-v2 dashboard-first + plan bar + modelo reseller LOCKED):** **DEBT-099 CERRADA** (base `ef60cfb` signup wizard · mig `00041` `6bab6a0` signup trigger idempotente · email template OMEGA `ff73922` · mig `00042` `2960000` clients CASCADE · toggle ojo password `c357dfe`) + **DEBT-099-v2 CERRADA** (`c578bdf` wizard opcional dashboard-first + `12dfed8` wizard inicial eliminado del repo · 6 archivos borrados · −230L · nudge dentro del Card Notificaciones · click → `/clients` · login global → `/dashboard` todos los roles · E2E confirmado producción ~07:33 AM 4 roles). **Plan status bar fix** (`55cc797`): 7 estados legibles + upgrade tier completo · "Renueva 26880d" eliminado. **DEBT-CONTENTLAB-422 registrada** (`837c40e` · 4h Sprint 8). **Higiene repo**: gitignore docs sensibles (`e91486e`+`19751e6`) · Stripe script env vars (`e9d81c0`). **SENTINEL brief diario confirmado prod 07:00** (score 86/100). **Modelo reseller LOCKED** (ver SOT §18 · DEBT-RESELLER-PORT ~80h Sprint 9+): 60/40 y 30% comisión eliminados · fee por tier sin comisión (Starter $3.5k/Growth $6.5k/Scale $12k) · OMEGA Company división de agentes verticales · ARIA cara/NOVA oculta · enforcement día 90. **7 DEBTs nuevas registradas Sprint 8+**: DEBT-CONTENTLAB-422 · DEBT-UI-POLISH · DEBT-LANDING-CMS · DEBT-RESELLER-PORT · DEBT-SCALE-POOL · DEBT-SCALE-CACHE · DEBT-SCALE-CDN · DEBT-SCALE-RATE · DEBT-SCALE-HORIZ. **Sprint 7 cerradas acumulado**: DEBT-105 + DEBT-FFMPEG-001/002/003/004 + DEBT-101 + DEBT-099 base+v2 (~52h netas de ~120h). **Sprint 7 abierto restante**: DEBT-097 (20h) · DEBT-096 (30h) · DEBT-102 (10h) · DEBT-088 (36h dep DEBT-040) · DEBT-033 (40h scope nuevo) + DEBT-LANDING-CMS (~30h).

> Detalle/contexto de cada una: `SOURCE_OF_TRUTH.md §6`. Aquí: ID · 1-línea · horas · dependencia · sprint.

### 🔴 CRÍTICAS (~80h)
| DEBT | Descripción | Horas | Dep. | Sprint |
|---|---|---|---|---|
| DEBT-040 | OAuth Meta + Google · **SKELETON 27 may** (`d9dac19` · 00037 oauth_tokens + Fernet + signed-state + 503 honesto) · falta creds owner + Meta App Review | ~40h restantes | creds owner | 5-6 |
| ~~DEBT-046~~ | ✅ **CERRADA** (`9efc230` · RONDA 1) reseller ve nivel ARIA real · migración 00033 (pendiente db push) · NEW reseller_aria.py · DEBT-063 cliente intacto | — | — | — |

### 🟠 ALTAS (~64h)
| DEBT | Descripción | Horas | Dep. | Sprint |
|---|---|---|---|---|
| ~~DEBT-050~~ | ✅ **CERRADA** (`1030abf` · RONDA 4 · opción A honesta) cero fabricación: monitor→real desde agent_executions/'unknown' · orchestrator→dispatch real · execute_agent fallback→501 sin persistir (P1 cerrado) · full-build ~16h NO construido (sin consumidor) | — | — | — |
| ~~DEBT-074~~ | ✅ **CERRADA** (`f06ecaa` · RONDA 2) safe_insert async (`await asyncio.to_thread`) · 20 call sites · best-effort intacto · gate 10/10 + guardian · required_insert queda como follow-up | — | — | — |
| ~~DEBT-048~~ | ✅ **CERRADA** (`625f089`) ARIA attention memory · voyage_adapter + 00036 (vector 1024d + find_similar_memories) + retrieval top-K con fallback cronológico · Voyage en whitelist I1 | — | — | — |
| DEBT-088 | Escalabilidad infra: job queue Redis/Celery (imágenes/videos) + multi-instancia Railway + ARIA rate-limit queue · 300→10K+ usuarios · ver §15 Capacidad | 36h | DEBT-040 | 7 |
| DEBT-092 | WhatsApp Business Add-On end-to-end (campo wizard + verificación Meta Cloud API + "Enviar por WhatsApp" + broadcast desde número del cliente + ARIA responde entrantes con voz de marca · reseller N clientes) · Básico $19/Pro $35 | 50h | RONDA D (OAuth Meta) | 8 |
| DEBT-093 | TikTok Full Integration (OAuth Login Kit + publicar video directo + chip Centro Inteligencia views/likes/shares/followers + Ads Manager básico + Publicador + analytics dashboard) · incluido PRO/Ent · Ads $25/mes | 30h | TikTok dev account | 8 |
| DEBT-094 | ARIA per-level pricing real (3 Stripe products por nivel + endpoint target_level + UI selector 4 niveles) · fix P1 ya aplicado (AriaUpgradeModal muestra solo el próximo nivel a precio real $12) | 6h | — | 8 |
| ~~DEBT-049~~ | ✅ **CERRADA** (b+c `093ffe2` · pendiente db push 00032 · a retirada en DEBT-083 `344e99f`: calendar_repository + NOVA path muerto eliminados) | — | — | — |
| ~~DEBT-080~~ | ✅ **CERRADA** (`37275ea`) código alineado a tabla agents real (status←is_active · cols reales · 500-traps resueltos) | — | — | — |
| ~~DEBT-081~~ | ✅ **CERRADA** (`8fd5d15`) omega/get_activity alineado · bloque agent_tasks eliminado | — | — | — |
| ~~DEBT-082~~ | ✅ **REGISTRADA+CERRADA** (`16c1df6`) omega/get_dashboard q_accounts+q_posts · omega 500-trap-free | — | — | — |
| ~~DEBT-083~~ | ✅ **CERRADA** (sweep `4e56a6c` 4 handlers + `ae8fc20` task_tracker→agent_executions + `344e99f` retira DUDA/calendar muerto · gate 10/10 · guardian audit · resellers-plural verificado limpio) | — | — | — |
| ~~DEBT-084~~ | ✅ **NUEVA+CERRADA** (`464ada3` · RONDA 1) ARIA multimodal: logo del cliente como image block a Claude · _logo_fetcher + _aria_multimodal · A2 puro · best-effort | — | — | — |
| ~~DEBT-047~~ | ✅ **CERRADA** (`31d0062`) persistent jobstore deploy-safe · SQLAlchemyJobStore con try/except fallback a memory store | — | — | — |
| ~~DEBT-038~~ | ✅ **CERRADA** (`067529f`) Stripe Customer Portal · `/billing/create-portal-session` + PaymentSection redirect · 503 honesto · pendiente activar portal en Stripe Dashboard | — | — | — |
| ~~DEBT-077~~ | ✅ **RESUELTA** (A `25ab75a`+migración 00031 agent_working_memory · pendiente db push · B→DEBT-049 · C `91adfff` dead-code eliminado) | — | — | — |
| ~~DEBT-064~~ | ✅ **CERRADA** (`d23c632`) router legacy `/content-lab` desmontado (paquete preservado para prompt_builder · frontend usa solo v3) | — | — | — |
| ~~DEBT-060~~ | ✅ **CERRADA** (`d83e0d1`) bucket `media` folder-scoped por `auth.uid()` (00035 · sin fuga cross-tenant) + Media.tsx namespacea bajo `{uid}/` | — | — | — |
| ~~DEBT-091~~ | ✅ **NUEVA+CERRADA** (`46a88e6`) checkout Agent Add-Ons Rex/Rafa/Maya Stripe real (6 prices · 503 honesto sin price) | — | — | — |
| ~~DEBT-095~~ | ✅ **NUEVA+CERRADA** (`d5a48b6`+`c583531`) trigger auto-provisión client_plans (00039) + backfill (00038) · aplicadas a prod | — | — | — |

### 🟡 MEDIAS (~22h)
| DEBT | Descripción | Horas | Dep. | Sprint |
|---|---|---|---|---|
| ~~DEBT-052~~ | ✅ **CERRADA** (`c2f26c7`→`d0c1922`·`67d1618`) créditos prepagados END-TO-END · FASE 4 (checkout 4 packs + enrolamiento + cron fin-de-mes + superadmin + auto-recarga) + FASE 5 widget AI Tab · follow-ups DEBT-089/090 · pendiente Stripe config owner | — | — | — |
| ~~DEBT-075~~ | ✅ **CERRADA** (`9e5c637`) `_is_public_host` compartido (rechaza loopback/RFC1918/metadata) en ambos fetchers antes del GET | — | — | — |
| ~~DEBT-087~~ | ✅ **CERRADA** (`34db708` · RONDA 5) agentic path → tabla `agents` real (code/is_active/system_prompt) · omega_activity→agent_executions · cero tablas fantasma | — | — | — |
| ~~DEBT-053~~ | ✅ **CERRADA** (`77da021` · RONDA 5) Posts Tab lee agent_executions client-scoped (RLS) · timeline por agente · empty-state honesto · cero fabricación | — | — | — |
| ~~DEBT-067~~ | ✅ **CERRADA** (`47c1837` · RONDA 1) generate_text +model · 12 agentes usan resolve_model · test 4/4 · bc_cognition intacto | — | — | — |
| ~~DEBT-076~~ | ✅ **CERRADA** (`6e7f735`+`c11b5ba` · RONDA 3) downgrade programado (Stripe SubscriptionSchedule + webhook plan-sync) + Enterprise self-serve (503 honesto) + computeLostItems cruza add-ons · gate 10/10 + guardian · **pendiente test staging Stripe** | — | — | — |
| ~~DEBT-078~~ | ✅ **RESUELTA** (`1635884` · migración 00030 REVOKE authenticated/anon · pendiente db push) | — | — | — |
| ~~DEBT-054~~ | ✅ **CERRADA** (`0946be5`) Info Tab muestra client_context dinámico | — | — | — |

### 🟢 BAJAS (~12.5h)
| DEBT | Descripción | Horas | Sprint |
|---|---|---|---|
| ~~DEBT-066~~ | ✅ **CERRADA** (26 may) header ClientDetail → cols reales business_email/website/industry | — | — |
| ~~DEBT-SEC-003~~ | → migrada a `SOURCE_OF_TRUTH.md` §6 (técnica · una deuda un hogar · 1 jun) | — | — |
| ~~DEBT-SEC-004~~ | → migrada a `SOURCE_OF_TRUTH.md` §6 (técnica · una deuda un hogar · 1 jun) | — | — |
| ~~DEBT-051~~ | ✅ **CERRADA (29 may · `32c49dd` · Fase 0b)** split a `aria_plan_repository.py` (fetch_live_plan) · aria_repository 100L exactos · C4 ok · gate 11/11 | — | — |
| DEBT-055 | Remover endpoint diagnóstico `run-now` (tras validar cron en prod) | 0.5h | — |
| DEBT-056 | `sentinel_check.sh` URL stale + Bearer · script X1 GET→POST+auth | 0.5h | — |
| DEBT-FK-CASCADE | 5 FKs hacia auth.users en NO ACTION (resellers.owner_user_id / upsell_requests.requested_by+approved_by / anti_fraud_signals.resolved_by / training_pairs.curator_user_id) · follow-up mig 00042 · una sola migración con 5 ALTER · ver SOT §6 | 1h | 8 |
| ~~DEBT-085~~ | ✅ **CERRADA** (`80db419`) build_client_context_block inyecta colores/fuentes de marca al contexto ARIA | — | — |
| ~~DEBT-086~~ | ✅ **CERRADA** (`80db419`) wizard muestra check verde + preview tras seleccionar logo | — | — |
| ~~DEBT-079~~ | ✅ **CERRADA** (`91b14d2`) writes muertos eliminados · cero readers · no se creó tabla | — | — |
| ~~Logo Fase 2~~ | ✅ **CERRADA** (vía DEBT-059) Persistir logo → `brand_files` + `client_brand_assets.logo_file_id` | — | — |

### 🆕 NUEVAS registradas 27 may (sesión 2 · detalle en SOT §6/§17 + docs estratégicos)
| DEBT | Descripción | Horas | Sprint |
|---|---|---|---|
| ~~DEBT-100~~ | ✅ **CERRADA** (`866a9d3`) evaluate_decisions · Loop 1 was_correct · cron horario · sin migración · **hallazgo P1**: source_event_id hoy→behavioral_events (forward-compatible · honesto) | — | 7 |
| ~~DEBT-099~~ | ✅ **CERRADA 28 may** (base `ef60cfb` signup + mig `00041` `6bab6a0` + email template `ff73922` + mig `00042` `2960000` + toggle ojo `c357dfe` · v2 `c578bdf`+`12dfed8` dashboard-first + wizard eliminado · E2E prod ~07:33 AM 4 roles) | — | 7 |
| DEBT-096 | 🟠 Página Estrategias ARIA (Básico 1/sem · PRO 3/sem · Enterprise 1/día · tabla strategies + cron + UI cards Usar/Archivar/Ajustar) | 30h | 7 |
| ~~DEBT-097~~ | ✅ **CERRADA (29 may · acotada)** Modo Supervisado (PRO/Enterprise) · `supervisado_mode_service.py` (P3 conf≥7 + P2 crisis fuera · importa limits_omega · SHA1 intacto) + endpoints supervisado (pending/reject/settings) · approve reusa `PATCH /content/{id}/save` (agent_memory ya cableado) · tab "Supervisado" en `/clients/:id` (por-negocio · gated PRO + CTA upgrade) + toggle en Config (`client_context.requires_publish_approval`) · **sin migración** · empty-state honesto. **Cron generador `strategy_generator` → DEBT-096** (otra fuente de drafts a la misma cola) | — | 7 |
| DEBT-098 | 🟠 Modo Autónomo (Enterprise opt-in · gates limits_omega · `autonomo_consent_at` · log) · dep OAuth | 30h | 8 |
| ~~DEBT-101~~ | ✅ **CERRADA** (`ef00fd0`) ARIA Learning Report semanal · cron lunes 07:05 UTC (5 min después oracle_weekly_brief) · 4 archivos nuevos (`aria_learning_report` 60L · `_aria_learning_formatter` 34L · `aria_learning_report_worker` 27L · test 59L 5/5) + extensión mínima `brief_dispatcher` (+6L · `dispatch_aria_learning_brief`) · agrupa `agent_memory` 7d por cliente: correct/incorrect/pending + top 3 agentes + training_pairs · skip silencioso si 0 actividad · cero migración · gate 10/10. NOVA Nivel 1 auto (mejoras brand_voice_corpus) queda follow-up separado | — | 7 |
| ~~DEBT-102~~ | ✅ **CERRADA (29 may · acotada a widget per-cliente)** tab "Aprendizaje" en `/clients/:id` · qué aprendió ARIA · lee `agent_memory` RLS solo evaluados (`was_correct IS NOT NULL` · pendientes aparte · P1) · empty-state honesto · **sin migración · SHA1 intacto** · 3 archivos (hook 75L + helper 65L + componente 75L · molde DEBT-053) + tab. **Cross-client `/superadmin/learning` + learning_events + migración → MOVIDO A DEBT-033** (RLS bloquea cross-client desde el front · necesita endpoint superadmin) | — | 7 |
| DEBT-103 | 🟠 collect_post_metrics Loop 2 (métricas reales Meta/Google) · dep DEBT-040 | 8h | 8 |
| DEBT-104 | 🟡 correction_detector conversacional (ARIA detecta correcciones en chat → memoria) | 6h | 8 |
| ~~DEBT-105~~ | ✅ **CERRADA** (`bae2b3d`) email owner: `brief_dispatcher`+`_brief_formatters` · SENTINEL diario (issues>0/score<85) + ORACLE semanal siempre · aislado de `alert_dispatcher` · best-effort · test 4/4 | — | 7 |
| ~~DEBT-FFMPEG-001~~ | ✅ **CERRADA** (`c9baba4`) `nixpacks.toml` con `nixPkgs = ["ffmpeg"]` | — | 7 |
| ~~DEBT-FFMPEG-002~~ | ✅ **CERRADA scope-acotado** (`c9baba4`) `_logo_overlay_video.py` (71L) con FFmpeg subprocess · overlay logo 15% width · 80% opac · esquina inf-derecha · 20px padding · best-effort (FFmpeg ausente → video original). **Las otras 9 ops del scope original (subs/música/trim/encode/etc) NO construidas** · registrar DEBT nuevo si se necesitan | — | 7 |
| ~~DEBT-FFMPEG-003~~ | ✅ **CERRADA** (`c9baba4`) `_video_compat` aplica overlay tras descarga + antes de upload via `apply_logo_to_video_bytes` (bridging bytes↔tempfile) | — | 7 |
| ~~DEBT-FFMPEG-004~~ | ✅ **CERRADA via metadata jsonb** (`c9baba4`) `logo_url` persiste en `video_generation_jobs.metadata` al insert · worker lo lee · **sin tabla nueva** · si se requiere audit table separada de jobs FFmpeg, registrar DEBT | — | 7 |
| ~~DEBT-FFMPEG-005~~ | → migrada a `SOURCE_OF_TRUTH.md` §6 (técnica · una deuda un hogar · 1 jun) | — | 8 |
| ~~DEBT-IMAGE-ASYNC~~ | → migrada a `SOURCE_OF_TRUTH.md` §6 (técnica · una deuda un hogar · 1 jun) | — | 8 |
| DEBT-CONTENTLAB-422 | 🟠 **NUEVA (28 may)** Content Lab HTTP 422 intermitente en gen de imagen (otras del mismo batch sí salen) · causa probable filtro Gemini / payload malformado / prompt fuera de límite en `nano_banana_adapter` · **incluye fix UX**: nunca mostrar "HTTP 422" crudo al cliente · copy honesto + botón reintentar single-item · producto en sí funciona (pulido, no estructural) | 4h | 8 |
| DEBT-UI-POLISH | 🟢 **NUEVA (28 may · sesión 6)** contenedor para pulidos visuales detectados en uso real · NO un DEBT específico · bucket de fixes pequeños UX (spacing/copy/tooltips/hover/focus/micro-animaciones) · cierre por lotes `polish(ui): ...` | TBD | 8+ |
| DEBT-LANDING-CMS | 🟡 **NUEVA (28 may · sesión 6)** editor super-admin de landing page (secciones/CTAs/fotos agentes/video hero) + white-label reseller generator (cada reseller con landing brandeada) · landing oficial `omega-landing-v3.html` local pendiente subir a Vercel | ~30h | 8-9 |
| DEBT-RESELLER-PORT | 🟠 **NUEVA (28 may · sesión 6)** portar modelo reseller LOCKED (ver SOT §18) al repo bajo DDD · **NO Lovable** · tiers Starter $3.5k/Growth $6.5k/Scale $12k · OMEGA Company verticales · Stripe Connect split · sidebar reseller (SEO/GEO/AEO · Paid Media · Centro Inteligencia avanzado · Benchmarks cross-client) · enforcement día 90 · monitoreo GUARDIAN+Finanzas→Ibrain. Bloqueado por resolver schema conflict `resellers` actual (60/40+30% legacy). Spec viva `Modelo_reseller_plan.md` local | ~80h | 9+ |
| DEBT-SCALE-POOL | 🟠 **NUEVA (28 may · sesión 6)** pgBouncer / connection pooling delante Supabase · evita `too many connections` con 100+ usuarios simultáneos · spec `Modelo_Escalabilidad.md` local | ~6h | 8 |
| DEBT-SCALE-CACHE | 🟠 **NUEVA (28 may · sesión 6)** Redis hot data (planes/features/limits/brand_voice) · TTL 5-15min ahorra ~70% lecturas Supabase · Upstash Redis + invalidación explícita en mutations | ~10h | 8 |
| DEBT-SCALE-CDN | 🟡 **NUEVA (28 may · sesión 6)** CDN para media (assets Supabase Storage · imágenes generadas · logos · video) · Cloudflare/Bunny edge cache · reduce egress Supabase | ~6h | 8 |
| DEBT-SCALE-RATE | 🟠 **NUEVA (28 may · sesión 6)** rate limits + back-pressure Anthropic/Gemini per-tier (Básico 10/min · PRO 30/min · Enterprise 100/min) · queue por cliente · back-pressure visible al cliente · complementa DEBT-070 | ~12h | 8 |
| DEBT-SCALE-HORIZ | 🟠 **NUEVA (28 may · sesión 6)** horizontal scaling Railway · multi-replica backend + LB + sticky session si websocket · revisión estado compartido · complementa DEBT-088 | ~12h | 8 |
| DEBT-MCP-ZERNIO | 🟠 **NUEVA (29 may · v2.0 Zernio · PRIMERA Sprint 8 sem 1)** proveedor de publicación · `zernio_adapter.py` + wizard paso 7 · 15 plataformas · MCP ejecutable · Meta Business Partner · 84% más barato que Ayrshare · `ZERNIO_API_KEY` ya en Railway · **LA BASE: sin publicar no hay datos que medir** · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.1 | ~12h | 8 |
| DEBT-HERMES-CORE | 🟠 **NUEVA (29 may · v2.0 · sem 1)** monitoreo de MCPs (conectividad/token expiry/quotas/alertas) · tabla `mcp_health_log` + RLS service_role · crons 5min/30min/6h/lun-07:05 · integra SENTINEL score · **1 constante nueva `limits_omega.py` `MAX_HERMES_ALERTS_PER_DAY_PER_MCP=3` → test-first + SHA1 rotation (G2)** · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.6 | ~14h | 8 |
| DEBT-MCP-ANALYTICS | 🟠 **NUEVA (29 may · v2.0 · sem 3 · cierra DEBT-034)** GA4+GSC OAuth + Zernio Analytics + Metricool → Supabase · alimenta Loop 2 (was_correct métricas reales) · **subsume el pipeline antes llamado DEBT-ANALYTICS-BRIDGE** · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.4 | ~10h | 8 |
| DEBT-ANALYTICS-BRIDGE | 🟠 **RE-DESCRITA (29 may · v2.0)** ya NO es "primera" · pipeline Zernio Analytics → Supabase **subsumido en DEBT-MCP-ANALYTICS (sem 3)** · Adspirer queda SOLO uso personal owner, no del sistema · spec `OMEGA_MCP_MASTER.md` v2.0 | ~8h (en MCP-ANALYTICS) | 8 |
| DEBT-AUTOFILL | 🟠 **NUEVA (28 may · sesión 6)** ARIA auto-llena Brand DNA del cliente desde su URL + Instagram via Firecrawl MCP → Claude analiza → auto-popula wizard · cliente confirma ~30s vs 10 secciones manuales · cierra fricción onboarding wizard detectada en uso real · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.3 (Firecrawl) | ~10h | 8 |
| DEBT-LUAN-PAID-MEDIA | 🟠 **NUEVA (28 may · sesión 6)** activar agente LUAN (paid media) via **Zernio Ads (Meta+Google+TikTok en 1)** + MCPs oficiales + BM Partner Access · **NO requiere App Review** (cliente agrega OMEGA como Partner en BM en 5min · una vez) · ARIA crea campañas desde Brand DNA + cliente aprueba en Supervisado (DEBT-097) · upsell PRO + Paid Media Management · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.2 + `META_GOOGLE_TOKENS.md` local | ~15h | 8 |
| DEBT-HERMES-FALLBACKS | 🟠 **NUEVA (29 may · v2.0 · sem 3)** cadenas de respaldo cuando un MCP cae · Firecrawl→BrightData→Playwright · Brave→Exa · Zernio queue · cache timestamp honesto · retry+backoff · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.6 | ~12h | 8 |
| DEBT-HERMES-UI | 🟢 **NUEVA (29 may · v2.0 · sem 4)** tab MCPs en Security panel (semáforo verde/amarillo/rojo · lee `mcp_health_log`) · **dep DEBT-033 base** · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.6 | ~8h | 8 |
| DEBT-MCP-INTEL | 🟡 **NUEVA (28 may · sesión 6)** stack inteligencia ARIA+NOVA: Trends MCP + Firecrawl + Exa + Tavily + Reddit MCP · datos reales trending por industria/región → contenido informado · NOVA Oracle Brief más preciso · cero acción cliente (lo activa owner) · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.3 | ~12h | 8 |
| DEBT-EDITOR-001 | 🟡 Editor video nativo (FFmpeg.wasm · timeline 4 capas · presets · brand auto) · por fases | 70h | 8-9 |
| DEBT-OMNI-001 | acción owner · early access Gemini Omni (aistudio · misma `GEMINI_API_KEY`) | 0h | — |
| DEBT-ARIA-UX | 🟡 **NUEVA (29 may)** bloque UX flujo Supervisado: grid 5×5 panel · clic→modal grande foto+caption+hashtags (absorbe P3) + Aprobar/Rechazar · Rechazar→tab Papelera en Contenido (recuperable) · toggle Supervisado de Configuración→tab por cliente · dep P2 backend · decisión: ¿ARIA genera imagen+hashtags? · atacar como bloque · spec SOT §6 | ~16h | post-P2 |
| DEBT-106 | 🟢 **Security Dev panel construido** (27 may) · `is_super_owner` (migr **00040** · pendiente db push) + gate `require_super_owner` (defense-in-depth · no toca auth_utils) + endpoints `/security-dev/{health,sentinel,guardian}` + tabs SENTINEL/GUARDIAN **reales** (empty-states honestos) + sidebar solo Ibrain. Subpartes **A/B/C/D** (Claude DEV Chat + Code Terminal E2B funcionales) → placeholders honestos con checklist real de 4 keys · **Sprint 8** | ~40h restantes (A-D) | 8 |

### Business backlog (sin estimar)
- DEBT-BIZ-001 pricing LATAM (Mercado Pago, Pix) · DEBT-BIZ-002 WhatsApp Business API · DEBT-BIZ-003 annual pricing · DEBT-BIZ-004 tier intermedio $39-45.
- "Nueva conversación" ARIA (botón archive del historial).

---

## 4 · ROADMAP SPRINTS

> Sprints 4B-6 cerrados/superados (DEBT-046/049/052/053 cerradas · OAuth pasó a SKELETON DEBT-040). Roadmap vigente 27 may sesión 2:

| Sprint | Foco | Incluye (~horas) |
|---|---|---|
| **Sprint 7** (~120h) | Learning loop + estrategias + onboarding + FFmpeg | DEBT-096 Estrategias (30) · DEBT-097 Supervisado (20) · DEBT-099 Self-service onboarding (20) · DEBT-033 Panel Superadmin UI (40 · scope nuevo · el DEBT-033 original ya cerrado) · DEBT-101 Learning Report (6) · DEBT-102 Learning Events UI (10) · DEBT-105 Email notifs (4) · DEBT-FFMPEG-001/002/003/004 (6.5) |
| **Sprint 8** (~190h) | Canales + autónomo + escala + Loop 2 | DEBT-092 WhatsApp ($19/$35 · 50) · DEBT-093 TikTok (Ads $25 · 30) · DEBT-098 Autónomo (30) · DEBT-088 Escalabilidad job queue (36) · DEBT-103 Loop 2 métricas reales (8) · DEBT-104 Correction detector (6) · DEBT-EDITOR-001 fase 1 (45) |
| **Sprint 9** (~70h) | Editor + pricing + reseller | DEBT-EDITOR-001 fases 2+3 (50) · DEBT-094 ARIA per-level pricing (6) · Reseller dashboard completo (40) |

### Orden recomendado próxima sesión
1. **Owner (no-código):** cargar creds OAuth (Meta/Google) + `OAUTH_ENCRYPTION_KEY` + `OAUTH_REDIRECT_BASE` → desbloquea DEBT-040 publicación real
2. **Owner (no-código):** registrar webhook Stripe + crear los productos/prices faltantes → activa checkout créditos/agentes/ARIA/Enterprise (hoy 503 honesto)
3. Código: DEBT-094 ARIA per-level pricing real (6h) · DEBT-051 split `aria_repository` (2h · preventivo C4) · DEBT-089/090 follow-ups créditos

> **Cerradas 25-26 may:** DEBT-042/054/057/058/059/061/062/063/065/066/068/069/070/071/072/073 + Logo Fase 2 (vía DEBT-059). El audit de rendimiento de imagen (068-071) quedó **totalmente cerrado**: uploads async, timeout, rate-limit y retry/backoff.

---

## 5 · DOCUMENTOS ESTRATÉGICOS EN RAÍZ

| Documento | Estado | Cuándo implementar |
|---|---|---|
| `ARIA_NOVA_INTELLIGENCE.md` | spec | guía de ARIA · vigente (referencia) |
| `BRAVE_OMEGA_INTELLIGENCE.md` | parcial implementado | full pendiente (Auto-Brave ya vive · falta el resto) |
| `SENTINEL_GUARDIAN_ENTERPRISE_COMPLETE.md` | spec | cuando haya 10+ clientes |
| `CENTRO_DE_INTELIGENCIA.md` | **no existe aún** | crear en Sprint 5 (DEBT-040) |
| `OMEGA_AGENT_SYSTEM.md` / `OMEGA_MULTI_AGENT_SYSTEM.md` | spec | arquitectura de agentes (referencia · P5 outcome_evaluator) |
| `DDD_REGLAS_OMEGA.md` | contrato vivo | gated · reglas C1-C4/A2/I1/G2/P1-P5/X3 |
| `ARIA_LEARNING_LOOP_OMEGA.md` | ✅ creado | loop de aprendizaje P5 · DEBT-100 (cerrada) / 101/102/103/104 |
| `WHATSAPP_BUSINESS_OMEGA.md` | ✅ creado (interno) | DEBT-092 WhatsApp Business Add-On |
| `TIKTOK_OMEGA.md` | ✅ creado (interno) | DEBT-093 TikTok Full Integration |
| `OMEGA_AUTONOMO_SUPERVISADO.md` | ✅ creado (interno) | DEBT-096/097/098 modos + Estrategias |
| `GEMINI_FFMPEG_OMEGA.md` | ✅ subido por owner | DEBT-FFMPEG-001..004 · DEBT-EDITOR-001 · DEBT-OMNI-001 |

---

## 6 · PROTOCOLO INICIO PRÓXIMA SESIÓN

```bash
git config --get user.email   # → raisenagencypr@gmail.com  (si no coincide: DETENER)
git log --oneline -5
curl https://omega-production-3c67.up.railway.app/health   # version · agents 37/37 · git_sha
```
Orden de lectura (`INDICE_PROYECTO.md`): `IDENTIDAD_GIT_CRITICA.md §2` → **`ESTADO_OMEGA.md`** (este · operacional) → `SOURCE_OF_TRUTH.md` (técnico) → Tier 2 según scope → últimos 5 episodios `agent_memory` (Supabase MCP) → **declarar intención y esperar confirmación**.

---

## 7 · REGLA DE CIERRE DE SESIÓN (un doc por tipo · "una deuda, un hogar")

Al cerrar cualquier sesión, cada cosa va a UN solo lugar (cero fuentes de verdad paralelas):

| Qué | Dónde | Regla |
|---|---|---|
| **Deuda técnica** (bug, limitación de código, infra, seguridad) | `SOURCE_OF_TRUTH.md` §6 | tabla canónica · es donde escribe el skill `registrar-deuda` |
| **Roadmap / rumbo / negocio** (pricing, features de producto, decisiones BIZ) | `ESTADO_OMEGA.md` (este) | estado operacional · qué está hecho/falta/orden |
| **Protocolos de verificación** (E2E manual, smoke tests) | docstring del código que validan | cerca del test · ej. los 4 tests ARIA viven en `test_message_client_scope.py` |
| **Narrativa de sesión / puesta-al-día entre instancias** | **documento-puente de un solo uso** | se genera AL CIERRE para la próxima sesión, se lee al inicio, y se **descarta** una vez absorbido. NO es doc permanente del repo (así fue el RECALL · puente cumplido y eliminado 1 jun) |
| **Mapa de lectura** | `INDICE_PROYECTO.md` | orden de tier · gates |

**NO crear docs de estado permanentes nuevos.** El puente de sesión es efímero por diseño:
nace al cierre, muere al absorberse. Cualquier doc que necesite una deuda → **apunta**
(`ver SOT §6`), no la copia. Si te encontrás copiando una deuda o un HEAD en un 2do lugar,
PARÁ: eso crea drift.

## 8 · REGLA: CERO JERGA TÉCNICA EN VISTAS DE CLIENTE (P1 + P2)

Toda vista de cara al cliente (PYME) renderiza **español de negocio**. CERO `snake_case`, CERO
`agent_code` crudo, CERO nombres de tabla/columna/evento internos, CERO nombres de archivo.
La verdad honesta (P1) se presenta en el idioma del cliente, no en el del código; mostrar jerga
cruda descuida su imagen del producto (P2).

- El mapeo crudo→etiqueta vive en `src/lib/*-labels.ts` (fuente única · patrón `learning-labels.ts`),
  NO en strings sueltos por el JSX. Crudo sin mapeo → fallback `humanize()` legible, nunca snake_case.
- **NOVA nunca se nombra al cliente** (es el cerebro interno · se muestra como "Tu asistente"/"ARIA").
- Implementado 1 jun en la pestaña Aprendizaje (`learning-labels.ts`). **Pendiente auditar otras
  vistas de cliente** con el mismo lente (seguimiento · no bloqueante).

---

🐢💎 No velocity. Only precision.
