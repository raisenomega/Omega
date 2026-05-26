# ESTADO OMEGA · Documento Vivo · Última actualización: 25 may 2026 (noche)

> **Fuente de verdad OPERACIONAL** (qué está hecho, qué falta, en qué orden).
> Fuente de verdad TÉCNICA (contratos DDD, arquitectura, detalle de DEBTs): `SOURCE_OF_TRUTH.md`.
> Este doc reemplaza los 8 `PENDIENTES_Y_PROGRESOS_*.md` (consolidados · detalle granular en git history).

---

## 1 · SISTEMA AHORA

| Componente | Estado | Identificador |
|---|---|---|
| Git HEAD | ✅ | `30375ff` al consolidar (correr `git log --oneline -1` para el vivo) |
| Frontend | ✅ Vercel | `omegaraisen.agency` (deploy auto en push a `main`) |
| Backend | ✅ Railway | `omega-production-3c67.up.railway.app` |
| Supabase | ✅ | proyecto `rwlnihoqhxwpbehibgxu` (PostgreSQL + RLS) |
| Migraciones | ✅ | `00001` → `00026` aplicadas (gap histórico en 00009 · sin pendientes) |
| Crons APScheduler | ✅ | **11/11** (incluye `outcome_evaluator` 4 AM · ver `DDD_REGLAS_OMEGA.md` X3) |
| Alertas Email (SENTINEL) | ✅ | Resend live · probado E2E 25 may 20:38 · `RESEND_API_KEY` puesta |
| Alertas Telegram | ⏸️ | Preparado · activa al pegar `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` (falta crear el bot) |

### Acciones owner pendientes (Railway env vars)
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` → activa Telegram (sin code deploy · el restart re-lee settings).
- `ALERT_EMAIL_FROM` (opcional) → cambiar de `onboarding@resend.dev` a un dominio verificado en Resend cuando lo tengas.

---

## 2 · DEBTs CERRADAS · ~50 total

> Detalle completo + hashes históricos: `SOURCE_OF_TRUTH.md §6` + `git log`. Resumen por sprint:

- **Sprint 1 (21 may):** Brand DNA Builder · ARIA memory · `prompt_vault`.
- **Sprint 2 (22 may):** persistencia Brand DNA (00017) · Virality Score · A/B variaciones · DEBT-018/019/020/044 · seguridad GUARDIAN 4B (00022).
- **Sprint 3 (23-24 may):** Content Lab completo (texto/imagen/video) · 20 DEBT-CL (003→022) · DEBT-VID-001 · DEBT-037 (ARIA Premium client) · DEBT-CL-017/018/020.
- **Sprint 4A (25 may):** SENTINEL subagent + builders · `input_sanitizer` · DEBT-002 analytics honesto · config fail-secure.
- **Sesión 25 may (día):** DEBT-031 (calendar legacy) · AUDIT 1/2 wizard% + picker · BUG A persistencia · wizard 3 fixes · 🔒 role server-side (`33166e4`) · hard-delete cliente · logo overlay Fase 1 · ARIA contexto ampliado.
- **Sesión 25 may (noche):** ARIA history DESC+reversed (`3a85fe1`) · ARIA deadlock input (`cece228`) · KPI Posts Programados (`44ca9d5`) · TAREA 2 popup 3 botones + 00025 `published_manual` · FIX P1 update_status (`84a05fe`) · FIX P5 conteos (`b2ab2fe`) · get_stats verde (`f807f2c`) · ISSUE 1 FK al agendar 409 (`59d182a`+`c9bfdb0`) · **outcome_evaluator 4A-2** (`5a834ed`+`3490ce0`+`8016531` · 00026) · **SENTINEL 8 endpoints superadmin** (`14b5d37`) · **alert_dispatcher** (`062353b`) · fix tablas fantasma sentinel (`91ad252`) · test regresión auth role (`f4c01b2`) · **DEBT-054 Info Tab → client_context** (`0946be5`) · consolidación docs → ESTADO_OMEGA único (`5858b12`+`92caa52`+`e8bdfcb`) · **Agente Publicador add-on** (`fd980ff`) · **DEBT-057+058 Tab AI → panel honesto Anthropic-only** (I1 · elimina multi-proveedor legacy + tablas fantasma) · **DEBT-059 logo wizard persiste** (`useUploadBrandLogo` · sube logo_files → `client_brand_assets.logo_file_id` · cierra overlay = Logo Fase 2 · P1) · **DEBT-061 crisis_manager guardrail P4** (`_assert_human_in_the_loop` enforza ACCIONES_PROHIBIDAS · `AUTONOMOUS_PUBLISH_ALLOWED=False` · model vía routing_table I2 · test G2 6/6) · **DEBT-066 + DEBT-072 + DEBT-073** familia "col inexistente" en clientes: header ClientDetail + tarjetas lista + buscador → cols reales (`business_email`/`website`/`industry`) · dot "activo" → `status === "active"` (antes `client.active` inexistente) · **DEBT-063** ARIA level real del backend (`max(plan, aria_level)`) → cliente que pagó Premium no ve "Actualizar" · **DEBT-062** social_accounts INSERT/render → cols reales (`approx_followers`/`status`) · CRUD "Agregar cuenta" destrabado · **DEBT-065** Tab Agente rediseñado a nivel ARIA del cliente + estado (`aria-levels.ts` compartido · sin legacy assigned_to) · **DEBT-042** regiones como chips con labels legibles en Info Tab (`REGION_LABELS` · `InfoRow.chips`) · **DEBT-068** uploads de imagen/video async vía `asyncio.to_thread` (+ overlay/find_logo · event loop no bloquea · P0 de escala) · **DEBT-069** timeout Nano Banana 90s (`asyncio.wait_for` → `ImageError("timeout")`) · **DEBT-070** rate-limit real (`RateLimitMiddleware` in-memory por IP · cablea `rate_limit_per_minute` · 429+Retry-After · antes config muerta) · **DEBT-071** retry+backoff de transitorios (429/5xx) en generación de imagen · 429 de Google → HTTP 429+Retry-After (antes 503 opaco).

---

## 3 · DEBTs ABIERTAS · ~190.5h (~5 semanas full-time)

> **Audit cliente E2E (25 may):** +10 DEBTs nuevas (057-066) · **DEBT-057/058/059/061 ya CERRADAS** (Tab AI Anthropic-only · logo wizard · crisis P4 · ver §2). % real cliente: core ~83% · superficie completa ~68%.
> **Audit rendimiento imagen (26 may):** +4 DEBTs (068-071) · **TODAS CERRADAS** (uploads async · timeout Nano Banana · rate-limit cableado · retry+backoff · ver §2). La generación de imagen ya no bloquea el event loop, no cuelga, está rate-limitada y reintenta transitorios.

> Detalle/contexto de cada una: `SOURCE_OF_TRUTH.md §6`. Aquí: ID · 1-línea · horas · dependencia · sprint.

### 🔴 CRÍTICAS (~84h)
| DEBT | Descripción | Horas | Dep. | Sprint |
|---|---|---|---|---|
| DEBT-040 | OAuth Meta + Google (Centro Inteligencia · publicación real) | 80h | — | 5-6 |
| DEBT-046 | ARIA Premium reseller variant ($25/mes · `resellers.addons`) | 4h | — | 4B |

### 🟠 ALTAS (~55h)
| DEBT | Descripción | Horas | Dep. | Sprint |
|---|---|---|---|---|
| DEBT-050 | Capa multi-agente stubeada (monitor/orchestrator/execute fabrican éxito · P1 cuando dispara) | 16h | — | — |
| DEBT-074 | `safe_insert` sync bloquea event loop (INSERTs inline · transversal · 5 repos · ~20 call sites) | 4h | — | — |
| DEBT-048 | ARIA attention memory + embeddings (Voyage · nueva excepción I1) | 16h | — | — |
| DEBT-049 | **PARCIAL** (b agent_executions 00032 + c agent_repository · `093ffe2` · pendiente db push) · queda (a) `calendar_repository` NOVA cols viejas | 3h | — | 4B |
| DEBT-080 | Drift Agent entity↔tabla agents (`find_all` .eq department/status + `omega/get_dashboard` select agent_id/department/status → 500 · la tabla solo tiene `code`) | 4h | — | — |
| DEBT-047 | APScheduler persistent jobstore (Python 3.13 + SQLAlchemy 2.0.25 incompat) | 4h | — | — |
| DEBT-038 | Stripe Customer Portal embed (PaymentSection) | 6h | — | — |
| ~~DEBT-077~~ | ✅ **RESUELTA** (A `25ab75a`+migración 00031 agent_working_memory · pendiente db push · B→DEBT-049 · C `91adfff` dead-code eliminado) | — | — | — |
| ~~DEBT-064~~ | ✅ **CERRADA** (`d23c632`) router legacy `/content-lab` desmontado (paquete preservado para prompt_builder · frontend usa solo v3) | — | — | — |
| DEBT-060 | Bucket `media` no existe en migraciones (galería rota) | 2h | — | 4B |

### 🟡 MEDIAS (~39h)
| DEBT | Descripción | Horas | Dep. | Sprint |
|---|---|---|---|---|
| DEBT-052 | AI Tab · créditos prepagados por agente (3 packs verticales · revenue) | 20h | DEBT-049 | 5 |
| DEBT-075 | SSRF host guard en fetchers de URL (web_scraper + fetch_url_tool · seguridad acotada) | 2h | — | — |
| DEBT-053 | Posts Tab · actividad por agente (cliente ve ROI) | 8h | **DEBT-049** | 5 |
| DEBT-067 | `claude_service` ignora model del agente → agents/ corre en Sonnet (I2 runtime · legacy) | 3h | — | — |
| DEBT-076 | Backend cambios de plan: downgrade programado a fin de ciclo + checkout Enterprise + computeLostItems cruce add-ons (no marcar Crisis Room si add-on $25) | 6h | — | 5 |
| ~~DEBT-078~~ | ✅ **RESUELTA** (`1635884` · migración 00030 REVOKE authenticated/anon · pendiente db push) | — | — | — |
| ~~DEBT-054~~ | ✅ **CERRADA** (`0946be5`) Info Tab muestra client_context dinámico | — | — | — |

### 🟢 BAJAS (~11h)
| DEBT | Descripción | Horas | Sprint |
|---|---|---|---|
| ~~DEBT-066~~ | ✅ **CERRADA** (26 may) header ClientDetail → cols reales business_email/website/industry | — | — |
| DEBT-SEC-003 | EXIF strip en imágenes subidas | 4h | — |
| DEBT-SEC-004 | Magic bytes verification (uploads) | 4h | — |
| DEBT-051 | `aria_repository.py` split (extraer `fetch_aria_context` · 99/100L) | 2h | — |
| DEBT-055 | Remover endpoint diagnóstico `run-now` (tras validar cron en prod) | 0.5h | — |
| DEBT-056 | `sentinel_check.sh` URL stale + Bearer · script X1 GET→POST+auth | 0.5h | — |
| ~~DEBT-079~~ | ✅ **CERRADA** (`91b14d2`) writes muertos eliminados · cero readers · no se creó tabla | — | — |
| ~~Logo Fase 2~~ | ✅ **CERRADA** (vía DEBT-059) Persistir logo → `brand_files` + `client_brand_assets.logo_file_id` | — | — |

### Business backlog (sin estimar)
- DEBT-BIZ-001 pricing LATAM (Mercado Pago, Pix) · DEBT-BIZ-002 WhatsApp Business API · DEBT-BIZ-003 annual pricing · DEBT-BIZ-004 tier intermedio $39-45.
- "Nueva conversación" ARIA (botón archive del historial).

---

## 4 · ROADMAP SPRINTS

| Sprint | Foco | Incluye |
|---|---|---|
| **Sprint 4B** | Revenue rápido + desbloqueos | DEBT-046 ARIA Premium reseller · DEBT-049 agent_executions (desbloquea DEBT-053) |
| **Sprint 5** | Centro de Inteligencia + tabs cliente | DEBT-040 (Google OAuth) · DEBT-052 AI Tab · DEBT-053 Posts Tab |
| **Sprint 6** | Meta Business | DEBT-040 (Meta OAuth · Instagram/Facebook publicación real) |
| **Sprint 7** | Google Ads | (post-Centro Inteligencia) |

### Orden recomendado próxima sesión (~18h)
1. DEBT-046 ARIA Premium reseller (4h) — revenue directo · única 🔴 abordable sin OAuth
2. DEBT-049 agent_executions (6h) — desbloquea DEBT-053
3. DEBT-053 Posts Tab (8h) — cliente ve ROI

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
