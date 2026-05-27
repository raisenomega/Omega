# PENDIENTES Y PROGRESOS · 27 may 2026

> Handoff de cierre de sesión · OmegaRaisen · 🐢💎 No velocity, only precision.
> Estado granular vivo: `ESTADO_OMEGA.md` · Deuda detallada: `SOURCE_OF_TRUTH.md §6` + `§16` (esta sesión).
> **La próxima sesión arranca con acciones del OWNER (creds OAuth + Stripe webhook/productos).**

---

## 0 · ARRANQUE PRÓXIMA SESIÓN → desbloqueos del OWNER (no-código)

Casi todo el código de revenue/publicación está cableado con **503 honesto** esperando config externa:
1. **OAuth (desbloquea DEBT-040 publicación real):** `META_APP_ID`+`META_APP_SECRET` · `GOOGLE_CLIENT_ID`+`GOOGLE_CLIENT_SECRET` · `OAUTH_ENCRYPTION_KEY` (`Fernet.generate_key()`) · `OAUTH_REDIRECT_BASE` en Railway. Más Meta App Review.
2. **Stripe:** registrar el webhook en el dashboard + crear los productos/prices faltantes → activa checkout de créditos/agentes/ARIA/Enterprise (hoy todos dan 503 honesto). Pasar a LIVE mode cuando esté listo.
3. **Código abordable sin owner:** DEBT-094 ARIA per-level pricing real (6h) · DEBT-051 split `aria_repository` (2h · preventivo C4) · DEBT-089/090 follow-ups de créditos.

---

## 1 · LO QUE SE HIZO HOY (todo pusheado a `origin/main` · ~40 commits · `c2f26c7`→`5a9856b`)

### DEBT-052 · créditos prepagados END-TO-END (5 fases · revenue)
- F1 migración 00034 `client_agent_credits` + ledger + RLS · F2 cost model (Micro$9/Starter$25/Plus$59/Ultra$119) · F3 enforcement 402 hard-block en texto+imagen.
- F4 (`c2f26c7`→`d0c1922`): checkout Stripe 4 packs · enrolamiento webhook · cron fin-de-mes (12º job · 00:05 · OMEGA retiene saldo · cero rollover) · superadmin mover/liberar · auto-recarga toggle (503 honesto sin Stripe · cero fabricación).
- F5 (`67d1618`): widget `ClientCreditsWidget` en AI Tab (saldo/periodo/pack/auto-recarga/consumo por agente · cero mocks).
- Follow-ups: **DEBT-089** (remover diagnostic `/system/credits/reset-now` tras validar cron) · **DEBT-090** (transfer superadmin no-atómico → RPC).

### DEBTs cerradas (Fork Mode · gate + guardian c/u)
- **DEBT-091** checkout Agent Add-Ons Rex/Rafa/Maya Stripe real (`46a88e6`)
- **DEBT-048** ARIA attention memory + Voyage AI (I1 excepción #3) · 00036 vector 1024d + `find_similar_memories` (`625f089`)
- **DEBT-047** APScheduler persistent jobstore deploy-safe (try/except → fallback memory) (`31d0062`)
- **DEBT-038** Stripe Customer Portal embed (`067529f`)
- **DEBT-060** media bucket folder-scoped por `auth.uid()` (fix cross-tenant del guardian · 00035) (`d83e0d1`)
- **DEBT-075** SSRF host guard `_is_public_host` en fetchers de URL (`9e5c637`)
- **DEBT-085 + DEBT-086** colores/fuentes → contexto ARIA + confirmación visual logo wizard (`80db419`)
- **DEBT-095** trigger auto-provisión `client_plans` + backfill (00038/00039) (`d5a48b6`+`c583531`)
- **LIMPIEZA TOTAL** · 34 archivos · legacy gpt-4/openai/Tavily removidos (avance DEBT-005/024/025)

### Progreso parcial (siguen abiertas)
- **DEBT-040 OAuth** SKELETON Meta+Google (`d9dac19`): 00037 `oauth_tokens` (Fernet) + signed-state CSRF + 503 honesto. Falta creds owner + Meta App Review.
- **RONDA E** Centro Inteligencia Fase 2 (chips reales) + auto-publicación esqueleto dormant (`0e1c073`).

### Stripe + scripts
- 16 productos activos (test mode) · 11 vars `STRIPE_PRICE_*` en Railway + `VOYAGE_API_KEY`.
- 4 scripts nuevos de provisioning (`771c685`): `create_stripe_enterprise/credit_packs/aria_premium/agent_addons.py`.

### UI/UX
- **Sidebar** rediseño: Principal [BÁSICO amber] + Avanzado [PRO azul] colapsables con locks · Add-Ons punto verde · scrollbar global oculta · trial 7 días desbloquea todo · Demo Mode PRO/Básico coherente (`31506b3`/`ba9afea`/`de2a37a`).
- **Tab Agente** 2 columnas (Nivel ARIA + chips tooltips + "Mejorar modelo ARIA" · "Añade Créditos" + "Añadir Créditos" · Agentes activos) (`c6f7543`). **Tab AI**: solo Motor de IA.
- **AriaUpgradeModal**: solo próximo nivel a precio real (fix P1 · `aded44b`) + chips informativos. **CreditPackModal**: 4 cards seleccionables + copy estratégica.
- **Add-Ons hub**: barra de estado top (chips ARIA + Mejorar ARIA + Añadir Créditos en la línea del título · `20f96ce`) + hover glossy amber en todas las cards (`5a9856b`).
- Fixes: guards demo removidos → Stripe real (`5542dfe`) · "Explorar Agentes" → `/add-ons#agentes` (`f6674e3`) · NOVA no visible al cliente en desc ARIA 4.0 (`bb3fcda`).

### Seguridad
- **Password DB rotada** por el owner + `DATABASE_URL` actualizada en Railway (tras la fuga del password en el error de psycopg2 de la sesión previa).

---

## 2 · MIGRACIONES — aplicadas a prod hoy (CLI `supabase db push --linked` · `rwlnihoqhxwpbehibgxu`)
`00034` client_agent_credits + ledger + RLS · `00035` SSRF/media (bucket folder-scoped) · `00036` ARIA attention memory (Voyage 1024d + find_similar_memories) · `00037` oauth_tokens (Meta+Google · Fernet) · `00038` backfill client_plans · `00039` trigger auto-provisión client_plans. Las pendientes-db-push previas (00030/00031/00032/00033) quedaron aplicadas en esta tanda. **Aplicadas hasta `00039` · cero pendientes.**

## 3 · DEBTs cerradas hoy
DEBT-052 (FASE 4/5 · –20h) · DEBT-091 (net0) · DEBT-048 (–16h) · DEBT-047 (–4h) · DEBT-038 (–6h) · DEBT-060 (–2h) · DEBT-075 (–2h) · DEBT-085 (–1h) · DEBT-086 (–0.5h) · DEBT-095 (net0). Confirmadas en prod (cerradas 26 may): DEBT-084/050/087/053.
Registradas hoy: DEBT-088 (escalabilidad · 36h · Sprint 7) · DEBT-092 (WhatsApp · 50h) · DEBT-093 (TikTok · 30h) · DEBT-094 (ARIA per-level · 6h · Sprint 8) · DEBT-089/090 (follow-ups créditos).
**Deuda total cumulative-open: ~734h** (–31.5h netas hoy · ver `SOURCE_OF_TRUTH §6`/`§16` y `ESTADO §3 ~127h`).

## 4 · ESTADO DEL SISTEMA
- **Backend** (Railway) + **Frontend** (Vercel) desplegados con todo lo de hoy.
- **Migraciones** hasta 00039 aplicadas · **12 crons** (incluye `reset_credit_periods` fin-de-mes).
- **Créditos prepagados**: sistema completo · self-service de compra/auto-recarga · 503 honesto hasta que el owner cree los productos Stripe.
- **OAuth**: estructura lista (tablas + handlers cifrados) · inerte hasta creds del owner.
- **ARIA** ahora usa memoria attention-based (Voyage) + ve el logo del cliente (multimodal) + conoce colores/fuentes de marca.
- Demo Mode (`cliente@omega.com`) puede llegar a Stripe checkout real (test mode) · toggle PRO/Básico se mantiene.

## 5 · DEUDA ABIERTA PRINCIPAL (orden sugerido)
1. **Owner**: creds OAuth + `OAUTH_ENCRYPTION_KEY` + `OAUTH_REDIRECT_BASE` → DEBT-040 publicación real.
2. **Owner**: webhook Stripe + productos/prices → activa checkout créditos/agentes/ARIA/Enterprise.
3. **DEBT-094** (🟡 6h) ARIA per-level pricing real (3 productos por nivel + UI selector).
4. **DEBT-088** (🟠 36h · Sprint 7) escalabilidad: job queue Redis/Celery + multi-instancia + ARIA queue.
5. **DEBT-051** (🟢 2h) split `aria_repository` (preventivo C4) · **DEBT-089/090** follow-ups créditos.
6. **Sprint 8 revenue**: DEBT-092 WhatsApp Business ($19/$35) · DEBT-093 TikTok (Ads $25).

## 6 · LEFTOVERS HONESTOS (🟢 · no bloquean)
- Checkout de créditos/agentes/ARIA/Enterprise + auto-recarga dan **503 honesto** hasta que el owner cree los productos Stripe (no es bug · es config externa pendiente).
- OAuth handlers dan **503 honesto** sin creds (estructura lista · inerte).
- `scripts/create_stripe_video_packs.py` quedó modificado en el working tree (no parte de los docs · revisar aparte).
- `legacy/` + `CENTRO_DE_INTELIGENCIA.md` + `SENTINEL_GUARDIAN_ENTERPRISE_COMPLETE.md` untracked (considerar `.gitignore` o commit deliberado).

---

> **Disciplina mantenida toda la sesión:** declarar antes de tocar · Fork Mode (subagentes escriben+validan · guardian audita · main integra) · gate `validate-before-push.sh` 10/10 c/u · 1 commit por módulo · staging explícito · push solo bajo pedido. 🐢💎
