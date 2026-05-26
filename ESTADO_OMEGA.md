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
- **Sesión 25 may (noche):** ARIA history DESC+reversed (`3a85fe1`) · ARIA deadlock input (`cece228`) · KPI Posts Programados (`44ca9d5`) · TAREA 2 popup 3 botones + 00025 `published_manual` · FIX P1 update_status (`84a05fe`) · FIX P5 conteos (`b2ab2fe`) · get_stats verde (`f807f2c`) · ISSUE 1 FK al agendar 409 (`59d182a`+`c9bfdb0`) · **outcome_evaluator 4A-2** (`5a834ed`+`3490ce0`+`8016531` · 00026) · **SENTINEL 8 endpoints superadmin** (`14b5d37`) · **alert_dispatcher** (`062353b`) · fix tablas fantasma sentinel (`91ad252`) · test regresión auth role (`f4c01b2`) · **DEBT-054 Info Tab → client_context** (`0946be5`) · consolidación docs → ESTADO_OMEGA único (`5858b12`+`92caa52`+`e8bdfcb`).

---

## 3 · DEBTs ABIERTAS · ~200h (~5 semanas full-time)

> **Audit cliente E2E (25 may):** +10 DEBTs nuevas (057-066 · ver tablas) · % real cliente: core ~83% · superficie completa ~68%. Las 🔴 críticas concentran las brechas que rompen promesa o violan reglas inviolables (Tab AI Solo-Anthropic, logo, crisis P4).

> Detalle/contexto de cada una: `SOURCE_OF_TRUTH.md §6`. Aquí: ID · 1-línea · horas · dependencia · sprint.

### 🔴 CRÍTICAS (~98h)
| DEBT | Descripción | Horas | Dep. | Sprint |
|---|---|---|---|---|
| DEBT-040 | OAuth Meta + Google (Centro Inteligencia · publicación real) | 80h | — | 5-6 |
| DEBT-046 | ARIA Premium reseller variant ($25/mes · `resellers.addons`) | 4h | — | 4B |
| DEBT-057 | **Tab AI viola Solo-Anthropic** (Lovable legacy · vende multi-proveedor) | 6h | — | 4B |
| DEBT-058 | Tab AI tablas fantasma (`ai_providers`/`client_ai_config`) | 0h | DEBT-057 | 4B |
| DEBT-059 | **Logo wizard no persiste** → "usar mi logo" no-op (P1) | 5h | — | 4B |
| DEBT-061 | crisis_manager sin guardrail P4 + model inválido | 3h | — | — |

### 🟠 ALTAS (~56h)
| DEBT | Descripción | Horas | Dep. | Sprint |
|---|---|---|---|---|
| DEBT-050 | Capa multi-agente stubeada (monitor/orchestrator/execute fabrican éxito · P1 cuando dispara) | 16h | — | — |
| DEBT-048 | ARIA attention memory + embeddings (Voyage · nueva excepción I1) | 16h | — | — |
| DEBT-049 | `agent_executions` inexistente + NOVA `infrastructure/calendar` schema fantasma | 6h | — | 4B |
| DEBT-047 | APScheduler persistent jobstore (Python 3.13 + SQLAlchemy 2.0.25 incompat) | 4h | — | — |
| DEBT-038 | Stripe Customer Portal embed (PaymentSection) | 6h | — | — |
| DEBT-062 | INSERT social_accounts escribe columnas inexistentes (CRUD roto) | 2h | — | 4B |
| DEBT-063 | ARIA Premium: cliente que pagó ve "Actualizar a 4.0" (comercial) | 1h | — | 4B |
| DEBT-064 | Routers legacy `/content-lab` colisionan (desmontar legacy) | 1h | — | — |
| DEBT-065 | `clients.assigned_to` inexistente · Tab Agente sin nivel ARIA | 2h | DEBT-033 | 4B |
| DEBT-060 | Bucket `media` no existe en migraciones (galería rota) | 2h | — | 4B |

### 🟡 MEDIAS (~31h)
| DEBT | Descripción | Horas | Dep. | Sprint |
|---|---|---|---|---|
| DEBT-052 | AI Tab · créditos prepagados por agente (3 packs verticales · revenue) | 20h | DEBT-049 | 5 |
| DEBT-053 | Posts Tab · actividad por agente (cliente ve ROI) | 8h | **DEBT-049** | 5 |
| DEBT-042 | Regions display en ProfileSection (chips vs string crudo) | 3h | — | — |
| ~~DEBT-054~~ | ✅ **CERRADA** (`0946be5`) Info Tab muestra client_context dinámico | — | — | — |

### 🟢 BAJAS (~14.5h)
| DEBT | Descripción | Horas | Sprint |
|---|---|---|---|
| DEBT-066 | Header ClientDetail cols inexistentes (email/company/phone) | 0.5h | 4B |
| DEBT-SEC-003 | EXIF strip en imágenes subidas | 4h | — |
| DEBT-SEC-004 | Magic bytes verification (uploads) | 4h | — |
| DEBT-051 | `aria_repository.py` split (extraer `fetch_aria_context` · 99/100L) | 2h | — |
| DEBT-055 | Remover endpoint diagnóstico `run-now` (tras validar cron en prod) | 0.5h | — |
| DEBT-056 | `sentinel_check.sh` URL stale + Bearer · script X1 GET→POST+auth | 0.5h | — |
| Logo Fase 2 | Persistir logo subido en Content Lab → `brand_files` + `client_brand_assets.logo_file_id` | 3h | 4B |

### Business backlog (sin estimar)
- DEBT-BIZ-001 pricing LATAM (Mercado Pago, Pix) · DEBT-BIZ-002 WhatsApp Business API · DEBT-BIZ-003 annual pricing · DEBT-BIZ-004 tier intermedio $39-45.
- "Nueva conversación" ARIA (botón archive del historial).

---

## 4 · ROADMAP SPRINTS

| Sprint | Foco | Incluye |
|---|---|---|
| **Sprint 4B** | Revenue rápido + desbloqueos | DEBT-054 Info Tab · DEBT-046 ARIA Premium reseller · DEBT-042 regions · Logo Fase 2 · DEBT-049 agent_executions (desbloquea DEBT-053) |
| **Sprint 5** | Centro de Inteligencia + tabs cliente | DEBT-040 (Google OAuth) · DEBT-052 AI Tab · DEBT-053 Posts Tab |
| **Sprint 6** | Meta Business | DEBT-040 (Meta OAuth · Instagram/Facebook publicación real) |
| **Sprint 7** | Google Ads | (post-Centro Inteligencia) |

### Orden recomendado próxima sesión (~27h · 3-4 sesiones)
1. DEBT-054 Info Tab (3h) — quick win · UX visible
2. DEBT-046 ARIA Premium reseller (4h) — revenue directo
3. DEBT-042 regions display (3h) — cosmético notable
4. Logo Fase 2 (3h) — completa feature ya empezada
5. DEBT-049 agent_executions (6h) — desbloquea DEBT-053
6. DEBT-053 Posts Tab (8h) — cliente ve ROI

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
