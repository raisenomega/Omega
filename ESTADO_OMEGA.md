# ESTADO OMEGA · Documento Vivo · Última actualización: 3 jun 2026 (**SPRINT 1 SENTINEL HARDENING** · HEAD `19b7717` · 7 capas en sesión: 4 CVE/dep-scan (`54727fb`) + 5 secrets-rotation (`e37fdec`) + 6 RLS-audit (`174f07d`) + 7-A AI-provider-router failover-prepared/Anthropic-only (`ffe4fdd`) + 9 observabilidad-runtime (`bd87b18`) + 10 performance-APM (`ac9429e`, cierra el error_rate de la 9) + 12 agentes-IA-health (`19b7717`) · migraciones 00050→00056 a prod · crons 16→21 · panel `/security-dev`→SENTINEL con 7 bloques nuevos data-real · regla P1 cada capa: verificar fuente antes de asumir (agent_log/omega_audit_log vacíos→fuentes reales · Railway/tokens ausentes→null honesto · cobertura legacy DEBT-023/024/025 siempre explícita) · pendiente próxima sesión: Capa 11 Integraciones · 3 Red/HTTP · 7-B Bedrock/Vertex (req creds AWS+GCP) · 8 Pentest · bridge GUARDIAN · spec viva local `SENTINEL_GUARDIAN_ENTERPRISE_COMPLETE.md` v2.1 gitignored · pendiente owner: disparar workflow GitHub `SENTINEL Build Stats` 1 vez) · 3 jun 2026 madrugada (HEAD `1816783` · panel SENTINEL final · chips clickeables + Ignorar/Fix funcional (migración 00049 `sentinel_issue_actions` aplicada) · Fix→Dev Chat existente (placeholder Sprint 8 · prompt copiable) · cero DEBT diferido) · 3 jun 2026 noche (HEAD `15f866a` · briefing fantasma fixeado (`aa23a1d`) + panel SENTINEL completo (botón scan + detalle per-componente HERMES style) · cero DEBT diferido) · 3 jun 2026 PM (HEAD `7627424` · SENTINEL des-cegado · migración 00048 + 3 filas reales E2E · DEBT-SENTINEL-BLIND CERRADA) · 3 jun 2026 (HEAD `36afac6` · CIERRE IDORs · #3 plan general · analytics `8b2da5e` + nova backend `715aab3` + página NOVA frontend `8262925` + iteraciones UX `6a0ce24`+`36afac6` · DEBT-IDOR-ANALYTICS + DEBT-IDOR-NOVA CERRADAS · auditoría 2-jun pusheada · 3 DEBTs nuevas registradas) · 1 jun 2026 PM (HEAD `a7a4d2d` · **HERMES v1.5 CERRADA** + **publicación Zernio construida F0→F3.6 y VERIFICADA EN VIVO** FB/IG/TikTok · DEBT-040 supersedida · DEBT-LIMIT1 `/publish/auto` cerrado · DEBT-IMAGE-ASYNC confirmada en vivo "se cae" · pendiente Zernio F4 rename + F5 wizard multi-negocio) · 1 jun 2026 AM (HEAD `cb585b6` · Switcher V1 CERRADO 100% + reconciliación censo · 4 deudas técnicas migradas a SOT §6 · regla de cierre de sesión añadida §7) · 29 may 2026 (Sprint 7 · DEBT-097 CERRADA · Modo Supervisado acotado: máquina estados P2/P3 + panel cola por-negocio + toggle · cron auto → DEBT-096 · DEBT-102 CERRADA widget "Qué aprendió ARIA" · cross-client → DEBT-033 · sync MCP v2.0 Zernio · DEBT-MCP-ZERNIO/ANALYTICS + 3 HERMES registradas · orden Sprint 8 re-locked) · 28 may 2026 (sesión 6 · DEBT-099+v2 CERRADAS · plan bar 7 estados · modelo reseller LOCKED · E2E prod ✅)

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
| Migraciones | ✅ | `00001` → `00047` aplicadas (2 jun · +`00046` `image_generation_jobs` async · +`00047` `zernio_account_id`/`handle` en `social_accounts` F5/2b · aditivas · ver `SOURCE_OF_TRUTH.md §16`+§18) |
| F5 Zernio per-negocio (backend) | ✅ (2 jun · `02e3de8`) | migración 00047 + 3 endpoints `/zernio` (GET available · POST map · DELETE unmap · `user_owns_client` en cada uno) + `resolve_account_id(platform, mapped)` backward-compat + HERMES global zernio (8 integ). **COMMIT 2 wizard frontend CANCELADO** (el onboarding existente ya conecta redes · construir wizard nuevo = redundante) · gap de cableado pendiente = **DEBT-ONBOARDING-ZERNIO-WIRE** |
| Seguridad · keys filtradas | ⏸️ rotar PRE-LAUNCH | 3 keys reales en `.env.example` versionado (ZERNIO · GOOGLE_CLIENT_SECRET · OAUTH_ENCRYPTION_KEY) · **DEBT-SECURITY-KEYS-ROTATION** · riesgo aceptado en desarrollo (repo privado) · rotar antes del 1er onboarding externo real |
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

═══════════════════════════════════════════════════════════════
## 🛡️ CIERRE SESIÓN 2 · TOTAL (3 jun 2026)

**Commits clave Sesión 2:** `4787b63` rework UX A · `ea9b533` rework UX B · `6ed7337` fix modal · `bbf0da4` Capa 3 Red/HTTP · `805aa42` CSP fix · `d54b5f1` Capa 11 Integraciones · `2d63acb` Capa 8 Chaos · `07b6ebf` cierre docs · `3f86c38` fix RLS prompt_vault · `12b4644` Capa 4 workflow · `46fdbef` Supabase Linter (12 issues) · **este commit** = cierre docs TOTAL.

**Estado SENTINEL final:** 13 componentes en `/security-dev` · 24 crons APScheduler · migraciones 00050→00064 · **~9.8/10 desde código** (máx alcanzable sin externos). GUARDIAN: **0/8 capas** (próximo Sprint).

**Score por capa:** Capa 1-2 (infra/code-audit) ✅ pre-Sprint1 · 3 (Red/HTTP) 100 ✅ · 4 (CVEs) 100 ✅ workflow verde · 5 (Secrets) 100 ✅ · 6 (RLS) 100 ✅ post prompt_vault · 7-A (AI router Anthropic) 100 ✅ · **7-B (Bedrock/Vertex) 🔴 BLOQUEADO (creds AWS+GCP owner)** · 8 (Chaos sin pentest) 100 ✅ · 9 (Observ) 100 ✅ · 10 (Perf) 100 ✅ · 11 (Integraciones) 100 ✅ · 12 (Agents Health) 100 ✅ · Hardening DB: 12/23 linter issues cerrados.

**Falta para 10/10 puro (NO depende de código):** 7-B (creds AWS+GCP) · pentest externo ($5-15k · DEBT-PENTEST-PROFESSIONAL) · Leaked Password Protection (upgrade Pro · DEBT abajo) · GUARDIAN 8 capas (~78h) · BRIDGE SENTINEL+GUARDIAN (~12h).

### 📋 DEBTs consolidados post-Sesión 2 (~28 OPEN)

**SENTINEL/Security-Dev (Sesión 2):** DEBT-024 (claude_service 48 callers · 12h 🟠) · DEBT-025 (ai_providers/dispatcher · 8h 🟠) · DEBT-070 (rate-limit→Redis · 6h 🟡) · DEBT-PREVIOUSLY-IGNORED-BADGE-V2 (3h 🟢) · DEBT-RATE-LIMIT-SYNTHETIC-TEST (3h 🟡) · DEBT-CSP-REPORT-RECEIVER (2h 🟢) · DEBT-CSP-STRICT (4h 🟡) · DEBT-STRIPE-WEBHOOK-E2E-TEST (3h 🟢) · DEBT-RESELLER-CONNECT-STATUS-COLUMN (2h 🟢) · DEBT-PENTEST-PROFESSIONAL ($5-15k 🟠 BLOCKED owner) · DEBT-CHAOS-FULL-COVERAGE (30h 🟢) · DEBT-WORKFLOW-ACTIONS-UPGRADE (30min 🟢) · DEBT-BANDIT-CONFIG-NOISE-EXCLUSIONS (30min 🟢) · DEBT-PROVISION-FUNCTIONS-REVIEW (3 trigger funcs · 30min 🟡) · DEBT-VECTOR-EXTENSION-SCHEMA-MOVE (2h 🟢) · DEBT-SENTINEL-LINTER-INTEGRATION (3h 🟠) · **DEBT-LEAKED-PASSWORD-PROTECTION-FREE-PLAN (🟡 ~5min · BLOCKED Free Plan)**.
**Heredados pre-Sprint1:** DEBT-002 (Math.random analytics 🟡) · DEBT-004 (202 archivos >75L 🟢) · DEBT-008 (frontend→Supabase directo 🟡) · DEBT-OWNERSHIP-TRIAGE 🟢 · DEBT-RESELLER-PATH-DEAD 🟡 · DEBT-ORPHANED-TABLES 🟢 · DEBT-ANTIFRAUD-WIRE 🟡 · DEBT-ENTERPRISE-PRICE-GUARD 🟢 · **DEBT-SCHEMA-DRIFT-RESELLER 🔴 BLOCKER** · DEBT-ROTAR-KEYS-PRELAUNCH 🟠 · DEBT-106A/B/C/D (Claude DEV ~40h 🟢) · DEBT-2FA-SUPERADMIN (4h 🟠 sugerido).

**DEBT-LEAKED-PASSWORD-PROTECTION-FREE-PLAN** 🟡 (~5min cuando upgrade) · Linter `auth_leaked_password_protection` (WARN) · **NO accionable en Free Plan** (requiere Pro ~$25/mes) · activar toggle Auth→Policies "Prevent use of leaked passwords" al upgrade pre-launch B2B · NO bloqueante MVP.

**RESOLVED Sesión 1+2:** DEBT-023 (model bump 18 may) · prompt_vault PERMISSIVE_TRUE+ASYMMETRIC (`3f86c38`) · Capa 4 workflow (`12b4644`) · 3 funcs SENTINEL exposed + 4 buckets + 5 search_path (`46fdbef`).
**Total OPEN: ~28 · ~70-90h pendientes (sin GUARDIAN/pentest) · ~158h + pentest + AWS/GCP para 10/10 completo.**

### 🎯 SESIÓN 3 · ARRANQUE GUARDIAN (0/8 capas · ~78h)
**Trilogía mínima (~22h · 1-2 sesiones · mayor valor):**
1. **Capa 1 · Zero Trust Identity por request** (~8h) · doc líneas 1292-1402 · `bc_cognition/application/guardian_identity.py` · re-valida identidad+permisos en CADA request · mapa endpoint→roles · default DENY.
2. **Capa 5 · Threat Score continuo** (~8h) · doc 1711-1806 · `guardian_threat_scorer.py` · score 0-100/user recalculado por acción · eficiente (no lookup costoso).
3. **Capa 6 · Respuesta proporcional** (~6h) · doc 1807-1876 · `guardian_response.py` · fricciones progresivas (rate-limit→email→bloqueo temporal→permanente) · NO romper flow legítimo.
**Complementaria (~56h):** Capa 2 behavior profiling 16h · Capa 3 Semantic Firewall 12h · Capa 4 Cross-Client Intel 12h · Capa 7 permanent memory 8h · Capa 8 forensic 8h + BRIDGE SENTINEL+GUARDIAN 12h.
**Migraciones estimadas:** 00065 guardian_identity_audit · 00066 guardian_threat_state · 00067 guardian_response_log · 00068+.
**PRIMERA ACCIÓN:** leer doc 1292-1402 → Plan Mode Capa 1 → checkpoint owner → aplicar.

### 📋 PENDIENTES MANUALES OWNER
✅ Sesión 2: SENTINEL Build Stats disparado · Dependency Scan verde post-fix.
🟡 No urgentes: marcar rotaciones base 10 secrets (Capa 5 baseline) · upgrade Free→Pro Supabase (Leaked Password Protection) · decisión pentest externo pre-launch.
🔴 Bloqueante Sesión 5+: credenciales AWS+GCP para Capa 7-B failover.
═══════════════════════════════════════════════════════════════


> **Audit cliente E2E (25 may):** +10 DEBTs nuevas (057-066) · **DEBT-057/058/059/061 ya CERRADAS** (Tab AI Anthropic-only · logo wizard · crisis P4 · ver §2). % real cliente: core ~83% · superficie completa ~68%.
> **Audit rendimiento imagen (26 may):** +4 DEBTs (068-071) · **TODAS CERRADAS** (uploads async · timeout Nano Banana · rate-limit cableado · retry+backoff · ver §2). La generación de imagen ya no bloquea el event loop, no cuelga, está rate-limitada y reintenta transitorios.
> **Sesión 27 may (marathon):** cerradas DEBT-052/091/048/047/038/060/075/085/086/095 (–51.5h) · DEBT-040 OAuth con SKELETON + RONDA E en progreso · DEBT-088/092/093/094 + 089/090 registradas (Sprint 7-8). Ver §2.
> **Sesión 27 may (sesión 2 · learning loop + estrategias/modos + FFmpeg + editor):** **DEBT-100 CERRADA** (`866a9d3` · Loop 1 was_correct · hallazgo P1 source_event_id documentado en SOT §6). Registradas DEBT-099/101/102/103/104/105 + FFMPEG-001..004 + EDITOR-001 + OMNI-001 (+ DEBT-096/097/098 ya en SOT §6). Total consolidado ~1,127h. Docs: `ARIA_LEARNING_LOOP_OMEGA.md` + `GEMINI_FFMPEG_OMEGA.md`. Ver tabla 🆕 abajo + SOT §17.

> **Sesión 27 may (sesión 3 · DEBT-105 email brief):** **DEBT-105 CERRADA** (`bae2b3d`) · brief al owner por email: `brief_dispatcher`+`_brief_formatters` (bc_cognition/application · aislados de `alert_dispatcher` por decisión del owner) · SENTINEL diario condicional (issues>0/score<85) + ORACLE semanal siempre · best-effort · test 4/4 · gate 10/10. **Security Dev panel ✅ desplegado** (migr 00040 + tabs SENTINEL/GUARDIAN reales + sidebar · `f0bc79c`/`d666bb4`) · subpartes A-D (Claude DEV chat/terminal) siguen abiertas (DEBT-106 · Sprint 8). **Sprint 7 restante:** DEBT-FFMPEG-001/002/003/004 (6.5h) · DEBT-096/097/099/101/102.

> **Sesión 27 may (sesión 4 · gate hardening + DEBT-FFMPEG):** **gate self-contained** vía 3 fixes (`bfa60c9` ROOT_DIR · `a6143f0` backend/conftest.py · `6c8a21a` CHECK 9 venv directo) → 10/10 desde shell limpio sin env/PATH. **DEBT-FFMPEG-001/002/003/004 CERRADAS** (`c9baba4`) logo overlay end-to-end imagen+video · `nixpacks.toml` con ffmpeg (001) · `_logo_overlay_video.py` FFmpeg subprocess 15%/80%/inf-derecha/20px best-effort (002, scope acotado a overlay) · `_video_compat` aplica tras download (003) · `logo_url` en metadata jsonb sin tabla nueva (004) · ratio imagen Pillow 10%→15% (alineado) · `apply_logo` cableado e2e: ContentLabFormV2 checkbox imagen+video · `useVideoJobPolling` payload · `GenerateVideoRequest` · handler + worker · 11 archivos · test 5/5 · gate 10/10.

> **Sesión 28 may (sesión 5 · DEBT-101 + parches):** **DEBT-101 CERRADA** (`ef00fd0`) ARIA Learning Report semanal · cron lunes 07:05 UTC · 4 archivos nuevos + extensión mínima `brief_dispatcher` (`dispatch_aria_learning_brief` 6L · mismo patrón que sentinel/oracle) · suite 144/144 (+5 nuevos). Bucket `brand-files` privado fix (`967f1a7`): `download_logo_bytes` via service-role en `_logo_overlay` resolvió "logo no persiste" (en realidad: 404 silencioso). Test-accounts enterprise perpetuo (`967f1a7` · cliente@omega + reseller@omega) + `useDemoMode` default `'enterprise'`. Wizard sección 9 (`68b7193`): thumbnail del logo previo con signed URL. **DEBT-IMAGE-ASYNC NUEVA** (`f5d44a1` · 🟠 10h Sprint 8) + timeout Nano Banana 120→180s parche temporal. **Sprint 7 cerradas acumulado**: DEBT-105 + DEBT-FFMPEG-001/002/003/004 + DEBT-101 (≈16.5h netas). **Sprint 7 abierto**: DEBT-099 (🔴 self-service 20h · próxima recomendada) · DEBT-097 (20h) · DEBT-096 (30h) · DEBT-102 (10h) · DEBT-033 (40h scope nuevo).

> **Sesión 28 may (sesión 6 · DEBT-099 self-service E2E + 099-v2 dashboard-first + plan bar + modelo reseller LOCKED):** **DEBT-099 CERRADA** (base `ef60cfb` signup wizard · mig `00041` `6bab6a0` signup trigger idempotente · email template OMEGA `ff73922` · mig `00042` `2960000` clients CASCADE · toggle ojo password `c357dfe`) + **DEBT-099-v2 CERRADA** (`c578bdf` wizard opcional dashboard-first + `12dfed8` wizard inicial eliminado del repo · 6 archivos borrados · −230L · nudge dentro del Card Notificaciones · click → `/clients` · login global → `/dashboard` todos los roles · E2E confirmado producción ~07:33 AM 4 roles). **Plan status bar fix** (`55cc797`): 7 estados legibles + upgrade tier completo · "Renueva 26880d" eliminado. **DEBT-CONTENTLAB-422 registrada** (`837c40e` · 4h Sprint 8). **Higiene repo**: gitignore docs sensibles (`e91486e`+`19751e6`) · Stripe script env vars (`e9d81c0`). **SENTINEL brief diario confirmado prod 07:00** (score 86/100). **Modelo reseller LOCKED** (ver SOT §18 · DEBT-RESELLER-PORT ~80h Sprint 9+): 60/40 y 30% comisión eliminados · fee por tier sin comisión (Starter $3.5k/Growth $6.5k/Scale $12k) · OMEGA Company división de agentes verticales · ARIA cara/NOVA oculta · enforcement día 90. **7 DEBTs nuevas registradas Sprint 8+**: DEBT-CONTENTLAB-422 · DEBT-UI-POLISH · DEBT-LANDING-CMS · DEBT-RESELLER-PORT · DEBT-SCALE-POOL · DEBT-SCALE-CACHE · DEBT-SCALE-CDN · DEBT-SCALE-RATE · DEBT-SCALE-HORIZ. **Sprint 7 cerradas acumulado**: DEBT-105 + DEBT-FFMPEG-001/002/003/004 + DEBT-101 + DEBT-099 base+v2 (~52h netas de ~120h). **Sprint 7 abierto restante**: DEBT-097 (20h) · DEBT-096 (30h) · DEBT-102 (10h) · DEBT-088 (36h dep DEBT-040) · DEBT-033 (40h scope nuevo) + DEBT-LANDING-CMS (~30h).

> **Sesión 3 jun (rework UX SENTINEL · Sub-bloque A + B):** **A** panel con 10 componentes (registry `sentinel_components_registry` + catálogo 10 cards + "Estado por componente" 10 filas expandibles que reusan los cards de detalle + secrets collapsible · `4787b63` · `SentinelRunsDetail` consolidado/eliminado). **B** chips clickables cross-component + modal universal (`loadIssuesBySource` rutea por source_type vía endpoints existentes · `buildFixPrompt` per fuente en frontend = single source · `[Ignorar]/[Fix]` persisten con `source_type`/`source_id` · migración **00057** `sentinel_issue_actions` +source_type/+source_id aplicada a prod · `issue_hash` SIN cambios para no romper el join legacy · cláusula visual: 6 cards aprobadas wrap limpio cero-cambio + 4 enriquecidas counts→chips con OK del owner). **DEBT-PREVIOUSLY-IGNORED-BADGE-V2 NUEVA** (🟡 ~3h Sprint 8+): el badge "previamente ignorado" hoy solo aparece en `sentinel_scan` (lo adjunta `get_history`); para las 7 fuentes nuevas falta endpoint GET-actions per `source_type` + lookup en frontend (hash compartido) para mostrar el flag en reapertura del modal.

> **Sesión 3 jun (Sprint 2 · Capa 3 Red y HTTP · 11º componente SENTINEL):** worker `network_http_2h` (22vo cron · minute=20 hour=*/2) chequea headers/TLS/rate-limit/CORS de `www.omegaraisen.agency` + Railway `/health`. `SecurityHeadersMiddleware` backend (HSTS/X-Frame/X-Content/Referrer/Permissions · NO CSP · outermost). CSP **Report-Only** en `vercel.json` (Supabase+Stripe+Google Fonts+Railway). Migración **00058** `sentinel_network_http_scans` a prod. 1er scan: frontend 97 (falta CSP→ahora Report-Only) · backend 85 (5 headers→ahora vía middleware) · TLS 1.3 ambos · rate-limit 300/min config · CORS hardened. Rate-limit verificado por **introspección de config** (no ráfaga · el worker corre EN Railway). **3 DEBTs nuevas:** `DEBT-RATE-LIMIT-SYNTHETIC-TEST` (🟡 ~3h · test e2e de efectividad real desde IP externa/GitHub Action cuando migremos a rate-limit Redis multi-instance) · `DEBT-CSP-REPORT-RECEIVER` (🟡 ~2h · endpoint que recibe CSP violations + persiste en `sentinel_csp_violations`) · `DEBT-CSP-STRICT` (🟡 ~4h · auditar/remover `unsafe-inline`/`unsafe-eval` tras 2 semanas de monitoreo Report-Only → promover a CSP enforced).

> **Sesión 3 jun (Sprint 2 · Capa 11 Integraciones · 12º componente SENTINEL):** worker `integrations_hourly` (23vo cron · minute=25) + migración **00059** (`sentinel_integrations_scans` + función `sentinel_webhook_idempotency_enforced()`). **Cierra X4 (monitoreo):** verifica en vivo que `webhook_events.event_id` tenga UNIQUE → 1er scan retornó `True`. Checks reescritos al schema REAL (el doc/plan asumían cols inexistentes): webhooks `event_count_24h` (no `processed`/`error`) + liveness desde `mcp_health_log[stripe]` (HERMES Capa 1 · **NO re-pinguea**) · Connect = count `resellers.stripe_account_id` · **OAuth desde `social_accounts` (19 reales · breakdown por platform)** NO `oauth_tokens` (skeleton vacío). 1er scan: **100/100 · 0 issues** (Stripe liveness ok · X4 enforced · 0 Connect · 19 social 0 conectadas/0 venciendo). MCP/Anthropic health NO duplicado (coverage_note → HERMES Capa 1 + Capa 7-A/12). **2 DEBTs nuevas:** `DEBT-STRIPE-WEBHOOK-E2E-TEST` (🟡 ~3h · test e2e de idempotencia con duplicado intencional vía Stripe webhook simulator) · `DEBT-RESELLER-CONNECT-STATUS-COLUMN` (🟢 ~2h · agregar `connect_status`+payout health a `resellers` para monitoreo Connect profundo · hoy solo se cuenta `stripe_account_id` present/null). Nota: fallos de handler de webhook solo quedan en logs (no persistidos en `webhook_events`); liveness sí vía HERMES.

> **Sesión 3 jun (Sprint 2 · Capa 8 mínima Chaos Engineering · 13º componente SENTINEL):** worker `chaos_monthly` (24vo cron · 1er lunes/mes 3AM) + on-demand vía `POST /sentinel/chaos/trigger`. Migración **00060** (`sentinel_chaos_scans`). **5 escenarios controlled (in-process/read-only · CERO daño prod):** anthropic_graceful_failure (generate agent inválido→ClaudeError sin API call) · db_error_handling (query tabla inexistente→error capturable) · stripe_idempotency (X4 read-only) · rls_isolation (lee Capa 6 sentinel_rls_audits · NO usa service_role que bypasea RLS) · rate_limit_effective (RateLimitMiddleware in-process→429 a limit+1). 3 catches técnicos reformularon el plan (service_role bypasea RLS · burst auto-bloquea worker en Railway · timeout flaky). 1er scan: **75/100 · 4/5 passed** · rls_isolation FAILED honesto (Capa 6 tiene 1 HIGH `prompt_vault PERMISSIVE_TRUE` preexistente). **Componente 2 (pentest profesional) = externo:** doc permanente committeado `PENTEST_CHECKLIST_OMEGA.md` (genérico OWASP · sin internals). Score Capa 8 ~7/10 desde código · 10/10 requiere pentest externo. **2 DEBTs nuevas:** `DEBT-PENTEST-PROFESSIONAL` (🟠 HIGH · servicio externo $5k-$15k USD semestral · firma HackerOne/Cobalt/NCC · ver `PENTEST_CHECKLIST_OMEGA.md` · necesario para certificación 10/10 SENTINEL) · `DEBT-CHAOS-FULL-COVERAGE` (🟢 ~30h · ampliar escenarios: Railway pod restart · Vercel CDN failover · Redis/cache · multi-region · cascading-failure prevention).

> **Fix Capa 4 Dependency Scan workflow (3 jun):** root cause = `bandit` + `npm audit --audit-level=high` salían exit 1 al ENCONTRAR CVEs (no "comando roto") → workflow rojo 3 runs + solo posteaba `status:failed` sin counts. Fix: scanners toleran findings (`|| true` + parse), workflow VERDE cuando corre, status derivado de severidad real (failed/warn/passed), payload enriquecido con counts+vulns por scanner; único hard-fail que queda = grep `service_role` en frontend (I1/G6). Card + loader + prompt builder muestran/normalizan cada CVE como issue clickable (ignore/fix). **CVE real detectado:** `vitest` critical CVSS 9.8 (GHSA-5xrq-8626-4rwp · dev-dep · solo con UI server activo · fix=major `vitest@4.1.8`) + 4 moderate (esbuild/vite/react-router). Python bandit: 8 low-noise (7×B108 /tmp en tests + 1×B104 bind 0.0.0.0 · benignos). **2 DEBTs nuevas:** `DEBT-WORKFLOW-ACTIONS-UPGRADE` (🟢 · checkout@v4/setup-python@v5/setup-node@v4 → v5+ cuando estables · no deprecadas hoy) · `DEBT-BANDIT-CONFIG-NOISE-EXCLUSIONS` (🟢 ~30min · `.banditrc` que excluya B108 en `tests/` + B104 en main.py con rationale). Pendiente owner: decidir bump major `vitest@4.1.8` (PR programado · no urgente: dev-only).

> **Fix Supabase Linter (3 jun · complementario a Capa 6 · migraciones 00062/00063/00064):** ✅ **12 issues cerrados, verificados a nivel DB** (psycopg2). **3 CRITICAL:** `REVOKE EXECUTE FROM anon/authenticated/PUBLIC` en `sentinel_rls_audit()` + `sentinel_slow_queries(int,int)` + `sentinel_webhook_idempotency_enforced()` (ACL post = solo postgres+service_role · backend usa service_role → cero impacto · Capa 6 sigue 0 issues). **4 HIGH (storage LIST):** avatars/generated-images/generated-videos → DROP broad `*_public_read` (getPublicUrl vía CDN intacto · buckets siguen public=true) · media → folder-scoped `(storage.foldername(name))[1]=auth.uid()` (preserva Media.tsx `.list()` propio · bloquea cross-tenant). **5 MEDIUM (search_path):** `set_updated_at` + `update_updated_at_column` + `invalidate_brand_dna_on_corpus_change` + `sentinel_endpoint_latency(int)` + `find_similar_memories(vector,text,uuid,int,float)` → `SET search_path=public,pg_temp` (0 funcs public no-extensión sin search_path post-fix). **3 DEBTs:** `DEBT-PROVISION-FUNCTIONS-REVIEW` (🟡 ~30min · 3 funcs SECURITY DEFINER+anon-exposed que son trigger functions: `auto_provision_client_on_signup`+`provision_client_plan`+`invalidate_brand_dna_on_corpus_change` · revisar caller real del signup flow + decidir revoke seguro) · `DEBT-VECTOR-EXTENSION-SCHEMA-MOVE` (🟢 ~2h · mover extensión `vector` de public a schema dedicado) · `DEBT-SENTINEL-LINTER-INTEGRATION` (🟠 ~3h · integrar Supabase Linter API como source adicional en Capa 6 worker · cobertura cross-vendor). **Acción manual owner (PASO 7):** activar "Leaked Password Protection" en Auth providers (cierra el último WARN del linter · auth_leaked_password).

> Detalle/contexto de cada una: `SOURCE_OF_TRUTH.md §6`. Aquí: ID · 1-línea · horas · dependencia · sprint.

═══════════════════════════════════════════════════════════════
### 🛡️ CIERRE SESIÓN 2 (3 jun 2026) · SENTINEL Sprint 1 + Sprint 2 consolidado

**Estado SENTINEL: 13 componentes · 24 cron jobs · panel `/security-dev` data-real.**
- **Sprint 1** (capas 4/5/6/7-A/9/10/12): dependency-scan · secrets-rotation · RLS-audit · AI-provider-router (Anthropic-only, Bedrock/Vertex pending creds) · runtime-observability · performance-APM · agents-IA-health.
- **Sprint 2** (capas 3/11/8 + rework UX A/B): Red-y-HTTP (headers+TLS+rate-limit+CORS · **100/100 en vivo**) · Integraciones (Stripe webhooks/Connect + OAuth · **100/100** · **cierra X4 monitoreo**) · Chaos-Engineering (5 escenarios controlled · **100/100 · 5/5 passed**). Rework UX: registry 13 componentes + modal universal + chips clickables cross-component (ignore/fix con `source_type`) + secrets collapsible.
- **Fix focal post-cierre (3 jun · migración 00061):** ✅ **CERRADO** el único HIGH+MEDIUM de Capa 6 — `prompt_vault` (tabla sistema, 36 prompts RAFA, sin tenant) tenía policy `authenticated USING(true)` que exponía la IP de prompts a todo user logueado. Hardened a **service_role-only** (DROP policy authenticated + CREATE service_role ALL · backend usa service_role/bypassa RLS · frontend no accede directo · cero-impacto funcional). Verificado en vivo: **Capa 6 → 0 issues** (0/0/0) · **Capa 8 chaos rls_isolation → passed · score 75→100**.
- Migraciones a prod Sprint 2: **00057** (issue_actions +source_type/+source_id) · **00058** (network_http) · **00059** (integrations + función X4) · **00060** (chaos).

**Reconciliación de duplicados/obsoletos (auditoría exhaustiva):**
- `DEBT-023` ✅ **CERRADA** (18 may, model bump) — el label "DEBT-023/024" del card AIProviders es impreciso (023 cerrada); el legacy claude_service vivo = **024**.
- `DEBT-024` (12h, 48 callers claude_service) y `DEBT-025` (8h, ai_providers/router/dispatcher) son **distintas, ambas OPEN, Fase 3** · NO duplican (paths distintos).
- `DEBT-070` ✅ (impl rate-limit) ↔ `DEBT-RATE-LIMIT-SYNTHETIC-TEST` (test e2e) = **complementarios**, no dup.
- `DEBT-CSP-REPORT-RECEIVER` (recibir violaciones) ↔ `DEBT-CSP-STRICT` (promover a enforced) = **complementarios**.
- Los 8 DEBTs nuevos de esta sesión son todos OPEN, ninguno duplica preexistentes.

**Tabla consolidada · DEBTs SENTINEL / Security-Dev (Área A):**

| DEBT | Estado | 1-línea | Horas | Sprint |
|---|---|---|---|---|
| DEBT-023 | ✅ RESOLVED | claude_service model bump (`18 may`) | — | — |
| DEBT-024 | 🟠 OPEN | 48 callers `claude_service` → `anthropic_adapter` único entry | 12h | Fase 3 |
| DEBT-025 | 🟠 OPEN | `ai_providers`/router/dispatcher → consolidar en routing_table+adapter | 8h | Fase 3 |
| DEBT-070 | ✅ RESOLVED | RateLimitMiddleware in-memory (`26 may`) | — | — |
| DEBT-PREVIOUSLY-IGNORED-BADGE-V2 | 🟡 OPEN | badge "ignorado" en las 7 fuentes nuevas (endpoint GET-actions + hash front) | 3h | 8+ |
| DEBT-RATE-LIMIT-SYNTHETIC-TEST | 🟡 OPEN | test e2e efectividad desde IP externa (post Redis multi-instance) | 3h | futuro |
| DEBT-CSP-REPORT-RECEIVER | 🟡 OPEN | endpoint CSP violations → `sentinel_csp_violations` | 2h | futuro |
| DEBT-CSP-STRICT | 🟡 OPEN | remover `unsafe-*` → CSP enforced (tras 2 sem report-only) | 4h | futuro |
| DEBT-STRIPE-WEBHOOK-E2E-TEST | 🟡 OPEN | test idempotencia duplicado intencional (Stripe simulator) | 3h | 8+ |
| DEBT-RESELLER-CONNECT-STATUS-COLUMN | 🟢 OPEN | `connect_status`+payout a `resellers` para Connect profundo | 2h | 8+ |
| DEBT-PENTEST-PROFESSIONAL | 🟠 OPEN | pentest externo semestral (no automatizable · `PENTEST_CHECKLIST_OMEGA.md`) | $5-15k ext | — |
| DEBT-CHAOS-FULL-COVERAGE | 🟢 OPEN | ampliar chaos (pod restart/CDN/Redis/multi-region/cascading) | 30h | futuro |
| SENTINEL-CAPA-7B-BEDROCK-VERTEX | 🔵 BLOCKED | failover Bedrock/Vertex · requiere creds AWS+GCP del owner | 6h | bloqueado-ext |

Subtotal Área A abierto: **~70h** + pentest externo ($) + 6h bloqueado. Áreas B (heredados pre-Sprint1), C (GUARDIAN ~78h, sistema aparte) y D (7-B bloqueado) → ver `SOURCE_OF_TRUTH.md §6` (ledger vivo) + `GUARDIAN_SECURITY_AGENT.md`.
═══════════════════════════════════════════════════════════════

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
| DEBT-MCP-ZERNIO | 🟡 **EN CURSO · CANAL VERIFICADO EN VIVO (1 jun · F0→F3.6 pusheadas)** — `zernio_adapter` + cableado "Publicar Auto"→Zernio publicando de verdad: FB texto ✅ · IG imagen ✅ · TikTok video ✅ (id real · visibilidad feed = privacidad TikTok) · fallo honesto ✅. F3.5 cerró slice DEBT-LIMIT1 `/publish/auto` (negocio activo validado). PENDIENTE: **F4** renombrar "Publicar Manual"→"Marcar como publicado" + **F5** wizard "Conectar redes" por negocio (2b) + HERMES zernio (8va integración). Detalle técnico vivo en `SOURCE_OF_TRUTH.md` §6 | F4 ~1h · F5 ~10h | 8 |
| DEBT-HERMES-CORE | 🟠 **NUEVA (29 may · v2.0 · sem 1)** monitoreo de MCPs (conectividad/token expiry/quotas/alertas) · tabla `mcp_health_log` + RLS service_role · crons 5min/30min/6h/lun-07:05 · integra SENTINEL score · **1 constante nueva `limits_omega.py` `MAX_HERMES_ALERTS_PER_DAY_PER_MCP=3` → test-first + SHA1 rotation (G2)** · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.6 | ~14h | 8 |
| DEBT-MCP-ANALYTICS | 🟠 **NUEVA (29 may · v2.0 · sem 3 · cierra DEBT-034)** GA4+GSC OAuth + Zernio Analytics + Metricool → Supabase · alimenta Loop 2 (was_correct métricas reales) · **subsume el pipeline antes llamado DEBT-ANALYTICS-BRIDGE** · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.4 | ~10h | 8 |
| DEBT-ANALYTICS-BRIDGE | 🟠 **RE-DESCRITA (29 may · v2.0)** ya NO es "primera" · pipeline Zernio Analytics → Supabase **subsumido en DEBT-MCP-ANALYTICS (sem 3)** · Adspirer queda SOLO uso personal owner, no del sistema · spec `OMEGA_MCP_MASTER.md` v2.0 | ~8h (en MCP-ANALYTICS) | 8 |
| DEBT-AUTOFILL | 🟠 **NUEVA (28 may · sesión 6)** ARIA auto-llena Brand DNA del cliente desde su URL + Instagram via Firecrawl MCP → Claude analiza → auto-popula wizard · cliente confirma ~30s vs 10 secciones manuales · cierra fricción onboarding wizard detectada en uso real · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.3 (Firecrawl) | ~10h | 8 |
| DEBT-LUAN-PAID-MEDIA | 🟠 **NUEVA (28 may · sesión 6)** activar agente LUAN (paid media) via **Zernio Ads (Meta+Google+TikTok en 1)** + MCPs oficiales + BM Partner Access · **NO requiere App Review** (cliente agrega OMEGA como Partner en BM en 5min · una vez) · ARIA crea campañas desde Brand DNA + cliente aprueba en Supervisado (DEBT-097) · upsell PRO + Paid Media Management · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.2 + `META_GOOGLE_TOKENS.md` local | ~15h | 8 |
| DEBT-HERMES-FALLBACKS | 🟠 **NUEVA (29 may · v2.0 · sem 3)** cadenas de respaldo cuando un MCP cae · Firecrawl→BrightData→Playwright · Brave→Exa · Zernio queue · cache timestamp honesto · retry+backoff · spec `OMEGA_MCP_MASTER.md` v2.0 Cat.6 | ~12h | 8 |
| DEBT-HERMES-UI | ✅ **v1.5 CERRADA (1 jun)** tab HERMES en `/security-dev`: semáforo verde/**amarillo**/rojo (amarillo derivado por umbral/integración) + detalle 3 líneas (último chequeo/último uso/operativa desde) + 7 links a consolas + tooltips §8. Backend sumó `created_at` (sin migración). NO dependía de DEBT-033 (falso). Historial de transiciones → DEBT-HERMES-UI-HISTORIAL (v2 · `SOURCE_OF_TRUTH.md`) | — | 0h (cerrada) |
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

---
---

# AUDITORÍA INTEGRAL OMEGA — 2026-06-02

> Auditoría read-only de reconstrucción de confianza. Método: workflow multi-agente (38 agentes · 1.9M tokens · 689 tool-uses · ~18 min) sobre 9 dominios + verificación adversarial de cada hallazgo MISSING/EXTRA + crítico de completitud. Repo `D:\Omega Master redes`, branch `master`, HEAD `17e513a`.
> **Regla seguida:** no asumir, verificar contra código (file:line / commit). Reportar con dureza honesta, sin defender.
> **Decisión owner (2 jun):** `ESTADO_OMEGA.md` es el ÚNICO documento operativo. SOT (`SOURCE_OF_TRUTH.md`) queda por compat histórica; en conflicto → gana ESTADO_OMEGA. Por eso esta auditoría vive acá, no en archivo separado.

## A0 · RESUMEN EJECUTIVO

**Veredicto de launch (del crítico adversarial):** **NO listo para el camino RESELLER. Condicionalmente listo para el camino CLIENTE-PYME-DIRECTO.**
- 1 cliente PYME directo ($29/$65 + adopción $0/7d): **probablemente funciona** — núcleo coherente doc↔código↔seeder.
- 1 reseller (modelo que el PRD declara primario): **rompe al crearlo y en cada vista de billing.**

**% construido (estimado):** PYME directo ~85-90% · Reseller economía ~10% · Visión (marketplace/regenerativo/WhatsApp/TikTok-nativo) ~5-15% · ARIA loops ~50%.

**Lo bueno (confirmado):** gate 11 checks real · 80/80 commit-hashes de §6 existen · 15/15 cierres muestreados tienen el fix · cero mocks reales en prod · `input_sanitizer` y OAuth Meta/Google reales.

**Lo crítico (bugs runtime confirmados):**
1. 🔴 **IDOR / cross-tenant:** `GET /analytics/dashboard/` (+ hermanos) sin auth, sin ownership, service_role → leak de datos de cualquier/todos los clientes.
2. 🔴 **Endpoints reseller billing/stats/detail/dashboard → 500** contra columnas inexistentes (`omega_commission_rate`, `monthly_revenue_reported`) en **5 handlers**.
3. 🔴 **Crear reseller falla** (INSERT a `clients` de `password_hash/role/subscription_status/trial_active` inexistentes, tragado por try/except → reseller sin login).
4. 🟠 **SENTINEL ciego** (tabla fantasma `sentinel_scans`) · **anti-fraude no cableado** (tabla sin código).
5. 🟠 **Schema drift prod-vs-migraciones SIN RESOLVER** — incógnita raíz; bloquea launch en ambas ramas.

## A · INVENTARIO
- **42 `.md` en raíz** (~26k líneas) · clusters duplicados (6 seguridad, 5 agentes, 2 identidad-git, 3 content-lab, 3 ARIA).
- **5 archivos pedidos inexistentes** (❌): `SOURCE_OF_TRUTH_MR.md`, `PENDIENTES_Y_PROGRESOS_20260524.md` (local-only), `OMEGA_VISION_10_ANOS_20260315.md`, `OMEGA_MODELO_COMERCIAL_20260315.md`, `OMEGA_Company_Precios_v3.docx`.
- **.claude/:** 8 agents, 4 skills, 3 hooks, settings×2 · `.claude/logs/` vacío en repo.
- **Código:** 659 `.py` backend · 316 `.ts/.tsx` (182 comp · 64 hooks · 18 pages) · 46 migraciones (00001→00047) · **141 tests backend vs 7 frontend** · 14 scripts.
- **Deudas:** 165 filas DEBT- en SOT §6 · 100 DEBT-refs en código · 3 TODO reales (1 accionable).

## B · RECONCILIACIÓN DOCS vs CÓDIGO (✅MATCH 🟡PARTIAL ❌MISSING 🔴EXTRA)

**B.1 Negocio/Pricing/Reseller:** ✅ 4 planes, $29/$65, adopción $0/7d, video packs, ARIA $12. 🟡 ENTERPRISE $199 (delegado a Stripe env, sin guard). 🔴 ARIA Premium Reseller $25 + Credit Packs (en código, no en doc). ❌ add-ons §4.2 (Crisis/CompIntel/SEO), packs volumen, split 30/70, split 60/40, mora reseller, marketplace B2B2B, columnas clients role/password_hash. **Conflicto visión:** PRD (factura solo a resellers) vs billing real (factura PYME directo).

**B.2 Arquitectura/DDD:** ✅ gate 11 checks, I1, G2/X2 SHA1, 16 crons. 🟡 A2 frontend sin enforce (glob `src/bc-*` vacío), C1/C4 grace-periods ~178 archivos, G9 mock=warning. ❌ A4 archivos inexistentes (`conviction.py`/`use_agent.py`/`memory_repository.py`), README muestra `src/bc-*` inexistente, `verify-on-stop.sh` NO verifica identidad (docs dicen que sí).

**B.3 Seguridad:** ✅ `input_sanitizer`, GUARDIAN login, RLS ~48 tablas. 🟡 PROTOCOLO 11 capas (rate-limit/lockout/token-revoke/GDPR ausentes), SENTINEL_ENTERPRISE 8 capas→3 agentes. ❌ SECURITY_SHIELD (DEBT-111..116, ~105h) 0%, SENTINEL SHIELD EASM 0%.

**B.4 ARIA/NOVA:** ✅ personas SHA1, 4 niveles, NOVA Opus, Loop 1, Context Builder pgvector, Brand DNA. 🔴 Fases 1-2 ya construidas (Plan Maestro dice "pendiente firma"). ❌ NBA Engine, cross_client_benchmarks, training_pairs writes, learning_events, Loop 2/3, nova_system_updater (tablas huérfanas / schema sin lógica).

**B.5 Content Lab/Publicación:** ✅ texto, A/B, vault 30 seeds, imagen+storage, imagen async F1-F4, video Veo3, Zernio FB/IG/TikTok, virality V1, RAFA. 🔴 Brave Research vivo (docs dicen mock). 🟡 TikTok solo proxy-Zernio, Brand DNA Score mide salud-corpus (no fidelidad-output). ❌ WhatsApp (0 código), TikTok nativo/analytics/Ads, Repurpose, get_suggestions/get_vault_prompts, columna ab_variant.

**B.6 Agentes/MCP/HERMES:** ✅ HERMES Capa 1, Brave, Meta+Google OAuth real, Zernio, GA4/GSC, SENTINEL crons, providers eliminados. 🟡 HERMES (doc 6 capas/8 crons → real 1 cron presencia-env), "8 agentes+SOPHIA" (real 37 legacy), oauth_tokens CHECK bloquea tiktok. ❌ SOPHIA meta-agente, Regenerativo/Agent Factory, MCPs Firecrawl/Exa/Tavily/Apify, MCPs Ads (LUAN), TikTok/WhatsApp OAuth, campaign_budgets/kill-switches, brave_adapter.py.

**B.7 BCs/Crons/Stripe:** ✅ bc-01/03/05/06/07, Stripe webhook idempotente (billing_v3), Email Resend live, Telegram preparado, Brand Voice+DNA. 🟡 crons=16 real, bc-04-analytics (actividad propia NO engagement de redes). ❌ endpoint `/system/cron-status`, "Stripe Connect" (mislabel — es Stripe estándar).

**B.8 Deudas:** ✅ 80 hashes existen, 15/15 cierres con fix, 13 migraciones citadas existen. 🟡 DEBT-047 cierre optimista (código sí, prod cae a in-memory), ~37 cierres sin hash (verificados). 🔴 silenciosas: CL-019/021/022, UPSERT-CLIENT-CLEANUP.

**B.9 Deuda silenciosa:** ✅ stubs honestos (DEBT-030/039/012), endpoints diagnóstico (DEBT-055/089), cero mocks reales, cero código-muerto. 🔴 `get_reseller_clients.py:61` `reseller_plan="agency_starter"` capa resellers a 5 clientes silenciosamente.

## C · DEUDAS RECONCILIADAS
Trazabilidad **sólida** (80/80 hashes, 15/15 fixes, 13/13 migraciones). Patrón de riesgo: **"fix commiteado" ≠ "fix en prod"** (testigo DEBT-047). Política de evidencia inconsistente (~80 con hash vs ~37 sin). 4 deudas silenciosas → inventario subcontado. No se verificaron las 165 una por una (alcance).

## D · DEUDA SILENCIOSA
TODO reales: **3** (no ~13; el resto = palabra española "todo"), 1 accionable (`agency_starter` cap-5). Mocks reales en prod: **0** (G9 = falsos positivos de comentarios "cero-mocks"). Código comentado muerto: **0**.

## E · CONTRADICCIONES ENTRE DOCS
1. **Crons: SOT=8, ESTADO=15, DDD/real=16.** ESTADO stale (off-by-one), SOT muy stale.
2. PRD (factura solo a resellers) vs MODELO_NEGOCIO+billing (factura PYME directo).
3. Add-ons §4.2 (Crisis/CompIntel/SEO) vs código (Rex/Rafa/Maya).
4. Temps A/B/C: MASTER §7.1 (0.7/1.0/0.4) vs §9.1 (1.0/0.4/1.2) vs código (0.4/0.7/0.9).
5. Brave: UI_V2/PLAN_100 "mock/diferido" vs código vivo.
6. ARIA Plan Maestro subestima (Fases 1-2 hechas) vs Learning Loop sobreestima (Loops 2/3/4).
7. "Stripe Connect" (SOT §1) mislabel.
8. A4/README listan archivos/`src/bc-*` inexistentes.
9. MCP_MASTER vs MCP_ARSENAL info contradictoria, sin índice de cuál supersede.

### E.1 · Contradicciones SOT vs ESTADO_OMEGA (qué migrar)
| # | SOT dice | ESTADO_OMEGA dice | Real | Migrar |
|---|---|---|---|---|
| 1 | §1 "8 cron workers" (apunta a main.py:72-85 inexistente) | §1 "15/15" | **16** | Corregir AMBOS a 16 + fix numeración inline main.py |
| 2 | §1 "Stripe Connect billing" → `billing/webhook.py` (desregistrado) | (no repite "Connect") | Stripe estándar (billing_v3 idempotente) | Quitar etiqueta "Connect" del SOT |
| 3 | §1 "Content Lab → `content_lab/handlers`" (legacy desmontado) | (fresco) | `content_lab_v3` | SOT §1 apunta a módulo muerto |
| 4 | §1 censo histórico stale (Stripe/crons/content-lab) | §1 más fresco (migraciones ya a 00047) | — | ESTADO ya es más confiable salvo crons |
| 5 | Interno SOT: DEBT-047 CERRADA **vs** DEBT-JOBSTORE-PERSISTENCE abierta | — | jobstore cae a in-memory en prod | Contradicción interna del SOT |
**Conclusión:** SOURCE §1 es censo histórico stale; ESTADO es más fresco salvo el conteo de crons. La consolidación SOT→ESTADO (Rec. #11) resuelve esto.

## F · RIESGOS DE SEGURIDAD
1. 🔴 **IDOR (CRÍTICO):** `analytics/router.py:177` + hermanos sin auth/ownership, service_role → leak cross-tenant.
2. 🟠 Sin defensa-en-profundidad (service_role bypassa RLS; aislamiento depende del guard por handler; analytics lo olvidó).
3. 🟠 Controles doc no implementados: rate-limit, account-lockout, token-revocation, failover LLM, GitHub Actions (`.github/` no existe), SHA1 worker.
4. 🟠 Anti-fraude NO cableado (tabla 00004 sin código) — superficie del trial $0/7d.
5. 🟠 SENTINEL ciego (tabla fantasma).
6. ✅ Secretos hardcoded: 0 (aparte de las 3 keys en historial → DEBT-SECURITY-KEYS-ROTATION, rotar pre-launch).

## G · EVALUACIÓN HONESTA
**¿Rompe si entra 1 cliente mañana?** PYME directo: probablemente OK. Reseller: rompe al crearlo + cada vista billing. **Primer quiebre, en orden:** (1) cualquier flujo reseller → 500/silent; (2) status warning/terminated → CHECK constraint; (3) Enterprise cobra lo que tenga el env; (4) abuso trial (sin detección activa); (5) rebuild desde migraciones → schema que el código reseller no corre = DR roto.

## RECOMENDACIONES PRIORIZADAS (TOP 11)
| # | Prio | Acción |
|---|---|---|
| 1 | 🔴 BLOCKER | Resolver schema drift prod-vs-migraciones (Supabase CLI linkeado a `rwlnihoqhxwpbehibgxu`; el MCP apunta al proyecto equivocado). |
| 2 | 🔴 HOY | Tapar IDOR analytics (auth + ownership en dashboard/analyze-metrics/dashboard-data/agent-status). |
| 3 | 🔴 | Arreglar o desactivar camino reseller (creación + billing/stats/detail/dashboard) hasta reconciliar schema. |
| 4 | 🟠 | Verificar `STRIPE_PRICE_ENTERPRISE`=$199 en Railway + guard que falle si vacío. |
| 5 | 🟠 | Cablear anti-fraude activo antes de abrir trial $0/7d a externos. |
| 6 | 🟠 | Arreglar SENTINEL `sentinel_scans`→`sentinel_risk_scores` (panel ciego). |
| 7 | 🟡 | Alinear doc de negocio con lo facturable (sacar/construir Crisis/CompIntel/SEO; agregar Rex/Rafa/Maya). |
| 8 | 🟡 | Hacer honestos docs aspiracionales (separar construido vs roadmap en HERMES/ARIA_LEARNING/SENTINEL_ENTERPRISE/AGENT_SYSTEM; marcar tablas huérfanas). |
| 9 | 🟡 | Corregir drift de tooling (crons→16, claim `verify-on-stop`, A4/README, borrar `billing/webhook.py` legacy). |
| 10 | 🟢 | Registrar deudas silenciosas (CL-019/021/022, UPSERT-CLEANUP, cap-5, DEBT-047 optimista) + regla "todo cierre lleva hash". |
| **11** | 🟡 | **Consolidar SOT → ESTADO_OMEGA: migrar toda info operativa de SOT que NO esté en ESTADO_OMEGA (ver §E.1). Eventualmente marcar SOT como ARCHIVADO.** (Decisión owner 2 jun · ESTADO_OMEGA = único doc operativo.) |

## NOTA DE HONESTIDAD SOBRE LA AUDITORÍA
La verificación adversarial **refutó la evidencia (no la conclusión)** de 2 hallazgos: `omega_commission_rate` SÍ existe en migración *legacy* (no en la canónica → el síntoma 500 se mantiene); `learning_events` aparece como cache-key en un hook (la tabla sigue sin construirse). El crítico subcontó el blast radius: las columnas fantasma se SELECTean en **5 handlers**, no 2. **Gaps no resueltos:** schema real de prod (no consultable read-only), dashboard reseller frontend, ausencia exhaustiva del marketplace.

## APÉNDICE — file:line de hallazgos críticos
- **IDOR analytics:** `analytics/router.py:177` + `analytics/handlers/get_dashboard.py`.
- **Reseller billing 500:** `get_reseller_billing.py:20`, `get_reseller_stats.py:19`, `get_reseller_detail.py:62`, `resellers/dashboard.py:54-55`.
- **Reseller creation:** `resellers/admin.py:85-91`, `:103-105`, try/except `:73-116`; `reseller_models.py:47-50`.
- **Reseller status CHECK:** `admin.py:194-213` vs `00001_initial_consolidated.sql:45`.
- **SENTINEL fantasma:** `sentinel_service.py:63` + `get_status.py:27`/`get_history.py:28`/`omega/_dept_report_security.py:13,29` (`sentinel_scans`; real `sentinel_risk_scores` 00029).
- **Cron cap reseller:** `get_reseller_clients.py:61-62`.
- **A4 inexistentes:** `DDD_REGLAS_OMEGA.md:114-128`; `README.md:106-119` (`src/bc-*`).
- **verify-on-stop:** `.claude/hooks/verify-on-stop.sh` (no valida identidad).
- **Tablas huérfanas ARIA:** `aria_nba_log`/`cross_client_benchmarks` (00008), `training_pairs` (00002, solo SELECT).

*Auditoría multi-agente · 2026-06-02 · embebida en ESTADO_OMEGA por decisión owner · NO pusheada (esperando lectura).*

---
---

# DIAGNÓSTICOS COMPLEMENTARIOS — 2026-06-02 (post-auditoría · read-only)

## Diagnóstico 1 — Scope real del IDOR

### 🔴 IDOR explotable SIN login (crítico)
**`/nova` (11 endpoints) — el peor:**
- `GET/POST /nova/context/{client_id}` (lee + **escribe** contexto del CEO Agent)
- `PATCH /nova/context/{client_id}/learning`
- `POST /nova/chat`, `/nova/execute-action`, `/nova/save-memory`
- **Sin auth en TODO el módulo** (cero `get_current_user`/`require_*`).
- Severidad: cualquiera **lee, modifica y ejecuta** acciones del CEO Agent de cualquier cliente, sin login.

**`/analytics` (7 endpoints):**
- `GET /dashboard/` agrega **TODOS** los clientes si no pasás `client_id`.
- `analyze-metrics`, `detect-patterns`, `generate-insights`, `forecast`, `dashboard-data`, `agent-status` — todos sin auth.
- Solo lectura — menos grave que nova, pero crítico igual.

### 🟠 Autenticados sin ownership explícito (triage pendiente)
`billing` · `brand_files` · `clients`(legacy) · `content_v3` · `context` · `oauth` · `omega` · `reseller` · `resellers` · `social_accounts` · `sub_brands`
- Requieren login pero NO verifican ownership del `client_id`.
- Posible cross-tenant para usuarios autenticados.
- ~11 módulos a triagear: algunos legítimos (super-admin, reseller-scope), otros IDOR-autenticado real.

### ✅ Falsos positivos descartados
- `agents` (stubs 501, DEBT-030) · `sentinel` (`require_superadmin` en cada handler) · `content_lab` legacy (no montado, DEBT-064).

## Diagnóstico 2 — Schema drift contra prod REAL

### Conclusión de fondo
**Prod COINCIDE con las migraciones canónicas. NO hay drift manual oculto.** Sistema reproducible desde migraciones · disaster-recovery OK.

### Drift identificado (acotado)
🔴 **`resellers` — 6 columnas que el código SELECTea pero FALTAN en prod:** `omega_commission_rate`, `monthly_revenue_reported`, `days_overdue`, `suspend_switch`, `clients_migrated`, `payment_due_date` → endpoints reseller billing/stats/detail/dashboard **rotos (500)**.

🔴 **`clients` — 5 columnas que `admin.py` INSERTa pero FALTAN en prod:** `password_hash`, `role`, `subscription_status`, `trial_active`, `email` → crear reseller **falla en runtime** (try/except traga el error → reseller sin login).

🔴 **`sentinel_scans` — tabla fantasma:** el código escribe/lee a `sentinel_scans` (no existe); la real es `sentinel_risk_scores` (existe pero no se usa) → **SENTINEL ciego** (panel muestra "todo OK" porque no hay datos).

✅ **Tablas huérfanas (existen en prod, 0 código las usa):** `anti_fraud_signals`, `aria_nba_log`, `cross_client_benchmarks`, `training_pairs` → decisión pendiente: borrar o usar.

✅ **`learning_events` — nunca se creó** (sospecha confirmada por la auditoría).

### Decisión de producto pendiente (NO de hoy)
Para arreglar reseller (#3/#4) + SENTINEL, hay 2 caminos:
- **CAMINO A — Construir economía reseller (semanas):** migración con las 6+5 columnas + lógica completa de billing/comisiones/stats + UI panel reseller funcional.
- **CAMINO B — Código honesto (días):** quitar referencias a columnas fantasma · desactivar/ocultar el camino reseller en UI hasta sprint dedicada · SENTINEL: cambiar `sentinel_scans`→`sentinel_risk_scores` en código.

CAMINO A = roadmap completo · CAMINO B = mitigación honesta. **Decisión del owner con cabeza fresca.**

---

## DEUDAS NUEVAS REGISTRADAS — 2026-06-02

✅ **DEBT-IDOR-NOVA** · ~~CERRADA 3-jun · `715aab3` backend (require_superadmin en los 11 endpoints) + página NOVA frontend `8262925` (super_owner-only) full-width + localStorage (últimos 50) + borde a borde (`6a0ce24`/`36afac6`)~~. (original) módulo `/nova` (11 endpoints) sin auth ni ownership. Lectura + escritura + ejecución de acciones del CEO Agent de cualquier cliente, sin login.

✅ **DEBT-IDOR-ANALYTICS** · ~~CERRADA 3-jun · `8b2da5e` (auth + ownership en los 7 endpoints + `GET /dashboard/` agg gated por require_superadmin)~~. (original) módulo `/analytics` (7 endpoints) sin auth. Lectura cross-tenant sin login; `GET /dashboard/` agrega TODOS los clientes si no pasás `client_id`.

🟠 **DEBT-OWNERSHIP-TRIAGE:** 11 módulos autenticados sin verificación explícita de ownership del `client_id`. Triage: separar legítimos (super-admin, reseller-scope) de IDOR-autenticado real. Lista en Diagnóstico 1. Trigger: después de los 2 críticos sin auth.

🔴 **DEBT-RESELLER-PATH-DEAD:** camino reseller roto en runtime (6 columnas faltantes en `resellers`, 5 en `clients`). Endpoints billing/stats/detail/dashboard → 500. Crear reseller falla silenciosamente. Decisión de producto pendiente: CAMINO A (construir, semanas) vs CAMINO B (código honesto, días).

✅ **DEBT-SENTINEL-BLIND** · ~~CERRADA 3-jun · migración 00048 (sentinel_scans materializada) + db push aplicado + E2E verificado: schema 11 cols + RLS service_role + POST /sentinel/scan/ 200 + 3 filas reales (VAULT/PULSE_MONITOR/DB_GUARDIAN) + /sentinel/status·history·deploy-check pueblan correctamente~~ + commit `7627424`. (corrección a la hipótesis de auditoría: NO era rename a `sentinel_risk_scores` — son modelos distintos; se materializó `sentinel_scans` per-agente, cero cambio de código). (original) SENTINEL escribe/lee a `sentinel_scans` (no existe). Panel ciego (siempre "todo OK").

🟢 **DEBT-ORPHANED-TABLES:** 4 tablas en prod sin uso de código: `anti_fraud_signals`, `aria_nba_log`, `cross_client_benchmarks`, `training_pairs`. Decisión: borrarlas (limpieza) o documentar por qué existen. No urgente.

### DEUDAS NUEVAS REGISTRADAS — 2026-06-03 (cierre IDORs)

🟠 **DEBT-ANTIFRAUD-WIRE** (~8h · pre-launch externo): la tabla `anti_fraud_signals` existe en prod (00004) pero 0 código la usa (confirmado auditoría 2-jun). El trial $0/7d sin detección de abuso es superficie de fraude (multi-cuenta · device fingerprint · patrones anómalos). Cablear: detectar signals típicas, INSERT en `anti_fraud_signals`, gate de creación de nuevos clientes flagged → require_superadmin manual. Trigger: antes del primer onboarding externo real.

🟢 **DEBT-ENTERPRISE-PRICE-GUARD** (~1h · pre-launch externo): hoy checkout Enterprise usa `STRIPE_PRICE_ENTERPRISE` del env. Si vacío/ausente Stripe cobra lo que tenga el env o devuelve error opaco. Falta guard explícito en startup que falle si no hay price ID Enterprise. Patrón ya usado en otros price IDs del repo. 1 línea defensive.

🔴 **DEBT-SCHEMA-DRIFT-RESELLER** (~4h · BLOCKER decisión reseller CAMINO A vs B): Rec #1 BLOCKER del auditor 2-jun. La MCP Supabase apunta al proyecto equivocado · schema real de prod (`rwlnihoqhxwpbehibgxu`) no consultable. Las 6 cols faltantes en `resellers` + 5 en `clients` la auditoría las dedujo del código (SELECT/INSERT), no del schema real. Acción: `supabase link --project-ref rwlnihoqhxwpbehibgxu` · `supabase db dump --schema public` · diff vs migraciones canónicas. SIN este step la decisión CAMINO A (construir, semanas) vs CAMINO B (código honesto, días) se toma a ciegas. Precondición de DEBT-RESELLER-PATH-DEAD.

*Diagnósticos read-only · 2026-06-02 · embebidos en ESTADO_OMEGA · NO pusheados (owner decide).*
