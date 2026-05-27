# ESTADO OMEGA · Documento Vivo · Última actualización: 27 may 2026 (sesión 2 · learning loop + roadmap Sprint 7-9)

> **Fuente de verdad OPERACIONAL** (qué está hecho, qué falta, en qué orden).
> Fuente de verdad TÉCNICA (contratos DDD, arquitectura, detalle de DEBTs): `SOURCE_OF_TRUTH.md`.
> Este doc reemplaza los 8 `PENDIENTES_Y_PROGRESOS_*.md` (consolidados · detalle granular en git history).

---

## 1 · SISTEMA AHORA

| Componente | Estado | Identificador |
|---|---|---|
| Git HEAD | ✅ | `5a9856b` (27 may · correr `git log --oneline -1` para el vivo) |
| Frontend | ✅ Vercel | `omegaraisen.agency` (deploy auto en push a `main`) |
| Backend | ✅ Railway | `omega-production-3c67.up.railway.app` |
| Supabase | ✅ | proyecto `rwlnihoqhxwpbehibgxu` (PostgreSQL + RLS) |
| Migraciones | ✅ | `00001` → `00039` aplicadas (27 may · créditos/SSRF/Voyage/oauth/client_plans · ver `SOURCE_OF_TRUTH.md §16`) |
| Crons APScheduler | ✅ | **12/12** (incluye `reset_credit_periods` 00:05 fin-de-mes · DEBT-052 · ver `DDD_REGLAS_OMEGA.md` X3) |
| Alertas Email (SENTINEL) | ✅ | Resend live · probado E2E 25 may 20:38 · `RESEND_API_KEY` puesta |
| Alertas Telegram | ⏸️ | Preparado · activa al pegar `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` (falta crear el bot) |

### Acciones owner pendientes (Railway env vars)
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` → activa Telegram (sin code deploy · el restart re-lee settings).
- `ALERT_EMAIL_FROM` (opcional) → cambiar de `onboarding@resend.dev` a un dominio verificado en Resend cuando lo tengas.
- **OAuth (desbloquea DEBT-040 publicación real):** `META_APP_ID`+`META_APP_SECRET` · `GOOGLE_CLIENT_ID`+`GOOGLE_CLIENT_SECRET` · `OAUTH_ENCRYPTION_KEY` (`Fernet.generate_key()`) · `OAUTH_REDIRECT_BASE`.
- **Stripe:** registrar el webhook en el dashboard + crear los productos/prices faltantes → activa checkout créditos/agentes/ARIA/Enterprise (hoy 503 honesto). Pasar a LIVE mode cuando esté listo.

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
| DEBT-SEC-003 | EXIF strip en imágenes subidas | 4h | — |
| DEBT-SEC-004 | Magic bytes verification (uploads) | 4h | — |
| DEBT-051 | `aria_repository.py` split (extraer `fetch_aria_context` · 99/100L) | 2h | — |
| DEBT-055 | Remover endpoint diagnóstico `run-now` (tras validar cron en prod) | 0.5h | — |
| DEBT-056 | `sentinel_check.sh` URL stale + Bearer · script X1 GET→POST+auth | 0.5h | — |
| ~~DEBT-085~~ | ✅ **CERRADA** (`80db419`) build_client_context_block inyecta colores/fuentes de marca al contexto ARIA | — | — |
| ~~DEBT-086~~ | ✅ **CERRADA** (`80db419`) wizard muestra check verde + preview tras seleccionar logo | — | — |
| ~~DEBT-079~~ | ✅ **CERRADA** (`91b14d2`) writes muertos eliminados · cero readers · no se creó tabla | — | — |
| ~~Logo Fase 2~~ | ✅ **CERRADA** (vía DEBT-059) Persistir logo → `brand_files` + `client_brand_assets.logo_file_id` | — | — |

### 🆕 NUEVAS registradas 27 may (sesión 2 · detalle en SOT §6/§17 + docs estratégicos)
| DEBT | Descripción | Horas | Sprint |
|---|---|---|---|
| ~~DEBT-100~~ | ✅ **CERRADA** (`866a9d3`) evaluate_decisions · Loop 1 was_correct · cron horario · sin migración · **hallazgo P1**: source_event_id hoy→behavioral_events (forward-compatible · honesto) | — | 7 |
| DEBT-099 | 🔴 Self-service onboarding (signup→wizard→checkout→workspace solo · **sin esto no escala**) | 20h | 7 |
| DEBT-096 | 🟠 Página Estrategias ARIA (Básico 1/sem · PRO 3/sem · Enterprise 1/día · tabla strategies + cron + UI cards Usar/Archivar/Ajustar) | 30h | 7 |
| DEBT-097 | 🟠 Modo Supervisado (PRO · ARIA prepara todo · cliente aprueba · panel + notificación) | 20h | 7 |
| DEBT-098 | 🟠 Modo Autónomo (Enterprise opt-in · gates limits_omega · `autonomo_consent_at` · log) · dep OAuth | 30h | 8 |
| DEBT-101 | 🟠 generate_aria_learning_report (reporte ARIA→NOVA semanal · NOVA Nivel 1 auto) | 6h | 7 |
| DEBT-102 | 🟡 learning_events + panel `/superadmin/learning` · migr 00041/00042/00043 (00040 reasignada a Security Dev · el número refleja orden real de aplicación, no reserva de sprint · ver DEBT-106) | 10h | 7 |
| DEBT-103 | 🟠 collect_post_metrics Loop 2 (métricas reales Meta/Google) · dep DEBT-040 | 8h | 8 |
| DEBT-104 | 🟡 correction_detector conversacional (ARIA detecta correcciones en chat → memoria) | 6h | 8 |
| DEBT-105 | 🟡 Email owner (sentinel_brief + oracle_weekly_brief → Resend/SendGrid) | 4h | 7 |
| DEBT-FFMPEG-001 | 🟠 FFmpeg en Railway (`nixpacks.toml`) | 0.5h | 7 |
| DEBT-FFMPEG-002 | 🟠 `ffmpeg_adapter.py` (10 ops: resize/overlay/subs/música/trim/encode) | 3h | 7 |
| DEBT-FFMPEG-003 | 🟠 integración post-Veo (brandeo automático logo/colores) | 2h | 7 |
| DEBT-FFMPEG-004 | 🟠 migración video_processing tables | 1h | 7 |
| DEBT-EDITOR-001 | 🟡 Editor video nativo (FFmpeg.wasm · timeline 4 capas · presets · brand auto) · por fases | 70h | 8-9 |
| DEBT-OMNI-001 | acción owner · early access Gemini Omni (aistudio · misma `GEMINI_API_KEY`) | 0h | — |
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

🐢💎 No velocity. Only precision.
