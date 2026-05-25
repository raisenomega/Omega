# PENDIENTES Y PROGRESOS · Sprint 3 cierre · 23-24 may 2026

> Sesión histórica. **19 DEBTs cerradas** + Brave Search + Stripe Video Packs +
> Upload context permanent + bug fixes UX. ~40 commits push verde.
>
> Doc consolidado del cierre completo del Sprint 3. PENDIENTES_20260523.md
> tiene el log granular de cierre por DEBT-CL · este doc es el handoff macro
> para próxima sesión.

---

## RESUMEN EJECUTIVO

Estado al cierre 24 may 2026 ~01:50 AST:

- **19 DEBTs cerradas** (17 DEBT-CL + DEBT-VID-001 + DEBT-039 V2 partial)
- **4 features nuevas** desplegadas: Brave Search Content Lab · Video Packs Add-Ons + Stripe Checkout · Upload context cliente permanent al system prompt · Multi-account picker
- **6 UX mejoras Content Lab** (UX-1 a UX-6) completas
- **Cero downtime** durante la sesión
- **Stripe Video Pack products** creados en test mode (3 productos · 3 price_ids)
- **Bugs latentes cerrados oportunistas**: `is_primary` ORDER BY en calendar/_access · `upgrade_aria.py` `result.ok` attribute access · handleSubmit silenciando zod errors

Métricas técnicas:
- ~40 commits firmados en main
- Pre-push hook 10/10 verde en todos
- tsc --noEmit limpio en cada commit
- Cero `any` introducido · cero `@ts-ignore`
- 2 migraciones SQL nuevas (00020 media_url · 00021 uploaded_context_*)
- Nuevos endpoints REST: `/billing/checkout-video-pack` · `/calendar-v3/schedule/` ·
  `/content-lab/research` · `/content-lab/improve-prompt` · `/clients/{id}/upload-context` ·
  `/clients/{id}/social-accounts` · `/content-lab/generate-video DELETE`

---

## 1 · DEBTs CERRADAS EN SPRINT 3 (orden de cierre)

| DEBT | Descripción | Commit cierre | Notas |
|------|-------------|---------------|-------|
| DEBT-CL-016 | ClientProfile model desincronizado (PlanOption +adopcion + 6 fields Optional) | `04567ac` | Bug 500 wizard Guardar/list |
| DEBT-CL-005 | Backend ignora client_id frontend (multi-client reseller) | `0f36425` + `769d362` | NEW _client_resolver.py |
| Wizard Guardar | `safe_insert` silenciaba writes críticos | `2d36666` | NEW required_insert helper |
| DEBT-CL-011 | Nano Banana ImageConfig re-activar SDK 2.6 | `3a504ec` | aspect_ratio honrado end-to-end |
| DEBT-CL-013 + (C) | useScheduleBlock + auth completa 4 endpoints calendar legacy | `91d99a8` | Cerró agujero seguridad CIA-level |
| DEBT-CL-017 + DEBT-031 partial | path X · NEW POST /calendar-v3/schedule/ + migración 00020 media_url | `d300117` + `dcf9389` | Schema V3 real (vs legacy mismatch) |
| DEBT-CL-018 | Bulk schedule N posts con spacer LIMITS_OMEGA | `155d4ae` | NEW _timestamp_spacer.py |
| DEBT-CL-015 + fix is_primary | Multi-account picker + bug latente ORDER BY col inexistente | `9ce37d1` | NEW GET /clients/{id}/social-accounts |
| DEBT-CL-019 | Brand DNA industry defaults fallback (8 verticales) | `891315f` | NEW domain/industry_defaults.py |
| DEBT-CL-012 | CORS download imagen/video · verificado OK sin código | `bb3257b` | Bucket Supabase public + auto CORS |
| DEBT-CL-010 + (B+a) | Video polling cancel + backend DELETE + cleanup auto | `86599d8` | Cerró agujero económico Veo |
| DEBT-CL-003 | Auth helpers ARIAChat + UpgradePlan + UpgradeBanner | `c2d4a03` | -59L netos · cierra bug auth missing |
| DEBT-CL-020 | PDF/DOCX/MD/TXT attachment per-request al system prompt | `7603929` | NEW _attachment_extractor.py + python-docx |
| DEBT-VID-001 + fix upgrade_aria | Stripe Video Pack Checkout + bug `result.ok` TypedDict | `6825e84` | 3 products en Stripe test mode |
| DEBT-CL-021 + DEBT-CL-022 | Auth helpers fuera cluster ARIA + GenerateContentSheet client_id | `af1dfcd` + `b34ba23` | -56L netos |
| **Brave Search feature** | NEW endpoint + cards UX en grid | `24afe0b` + `db3aa58` + `aff6ecf` | Botón Research cableado |
| **Upload context permanent** | Doc cliente persistente inyectado al system prompt RAFA | `2dd5eb4` | Cierra DEBT-039 V2 partial · migración 00021 |
| Bugfix · scrollbar textarea | CSS Tailwind arbitrary [scrollbar-width:none] | `b8e2811` | + script create_stripe_video_packs.py |
| Bugfix · handleSubmit zod silencioso | onInvalid callback con toast destructive + console.warn | `cac7e21` | Wizard Guardar Cambios visible |

### Status DEBT-CL final post-Sprint 3

| ID | Status |
|----|--------|
| DEBT-CL-003 | ✅ CERRADA |
| DEBT-CL-005 | ✅ CERRADA |
| DEBT-CL-008 | ✅ CERRADA |
| DEBT-CL-009 | ✅ CERRADA |
| DEBT-CL-010 | ✅ CERRADA |
| DEBT-CL-011 | ✅ CERRADA |
| DEBT-CL-012 | ✅ VERIFICADA OK |
| DEBT-CL-013 | ✅ CERRADA |
| DEBT-CL-014 | ✅ CERRADA (sesión anterior) |
| DEBT-CL-015 | ✅ CERRADA |
| DEBT-CL-016 | ✅ CERRADA |
| DEBT-CL-017 | ✅ CERRADA |
| DEBT-CL-018 | ✅ CERRADA |
| DEBT-CL-019 | ✅ CERRADA |
| DEBT-CL-020 | ✅ CERRADA |
| DEBT-CL-021 | ✅ CERRADA |
| DEBT-CL-022 | ✅ CERRADA |
| DEBT-VID-001 | ✅ CERRADA |
| DEBT-031 | 🟡 partial (path write V3 OK · read legacy aún broken) |
| DEBT-039 | 🟡 partial (V2 upload context cerrado · V1 auto-populate wizard pendiente) |
| DEBT-040 | 🔴 abierta (OAuth flows · Sprint 4+) |
| DEBT-042 | 🔴 abierta (regions display ProfileSection) |
| DEBT-046 | 🔴 abierta (ARIA Premium reseller variant) |
| DEBT-047 | 🔴 abierta (persistent jobstore Python 3.13 + SQLAlchemy) |
| DEBT-048 | 🔴 abierta (ARIA attention-based memory · embeddings + I1 excepción) |

---

## 2 · FEATURES NUEVAS DESPLEGADAS

### 2.1 Video Packs Add-Ons + Stripe Checkout (DEBT-VID-001)

- **Modelo de pricing** documentado en `MODELO_NEGOCIO_OMEGA_CLIENTE.md §4.4`:
  - Pack Starter $39/mes · 6×8s
  - Pack Creator $95/mes · 5×30s
  - Pack Cinematic Pro $125/mes · 3×60s
- **Página `/add-ons`** con 3 cards comparativas · botón "Activar Pack" amber
- **NEW endpoint** `POST /api/v1/billing/checkout-video-pack` · plan check basic/pro · 1 pack a la vez
- **Stripe Products creados** en test mode (ver Acciones Manuales sec 4)
- **NEW** `bc_billing/application/create_video_pack_checkout.py` · `_addon_handlers.handle_video_pack_activation`
- **Frontend** `useVideoPackCheckout` + AddOnsPage wire real
- **BONUS fix latente** `upgrade_aria.py:40` `result.ok` (BillingResult TypedDict no dataclass)

### 2.2 Brave Search Content Lab

- **NEW endpoint** `POST /api/v1/content-lab/research` · auth + delegate a `web_search_tool.web_search()`
- **Frontend** `useResearch` hook + cards research en el grid (no panel inline)
- **UX**: input "Research" verde · click → cards azules en el grid · "Usar snippet" appendea al topic
- **Persistencia** localStorage (las cards sobreviven refresh igual que generadas)
- **Errores HTTP**: 503 brave_not_configured · 503 brave_timeout · 503 brave_unavailable

### 2.3 Upload Context Permanent (DEBT-039 V2)

- **Migración 00021** `client_context.uploaded_context_text/filename/mime/at`
- **NEW endpoint** `POST /api/v1/clients/{id}/upload-context` · multipart file
- **Reusa** `_attachment_extractor.py` (DEBT-CL-020) para PDF/DOCX/MD/TXT
- **Inyección** al system prompt RAFA: `# CONTEXTO PERMANENTE DEL CLIENTE (documento adjunto)`
- **Frontend** SectionSamples wizard step 10 · disabled hasta cliente creado
- **NEW** `useUploadClientContext` hook + `apiPostFormData` multipart helper

### 2.4 6 UX Mejoras Content Lab

| UX | Descripción | Commit |
|----|-------------|--------|
| UX-1 | Loading state cableado al botón Generar | `ba74667` |
| UX-2 | Botón ✨ Mejorar Prompt (Claude Haiku · DDD I2) | `4345fdd` |
| UX-3 | Aspect ratio selector imagen/video · cierra DEBT-CL-008/009 | `8dbbad8` |
| UX-4 | Variation labels compactos 1 línea horizontal | `7318b13` |
| UX-5 | Verificación BRAVE_API_KEY (reporte read-only) | — |
| UX-6 | Upload imagen referencia (type=image · base64 → Nano Banana) | `4bf3bd2` |

### 2.5 Multi-Account Picker (DEBT-CL-015)

- Cliente con 2+ cuentas IG/FB/etc → dropdown "— Cuenta —" en form bar
- NEW `GET /api/v1/clients/{id}/social-accounts?platform=X`
- Cero leak access_tokens (filter cols)
- Fallback automático: si user no elige → primera cuenta active por created_at

### 2.6 Bulk Schedule N Posts (DEBT-CL-018)

- POST `/calendar-v3/schedule/` ahora acepta `content_ids: list[str]` (era singular)
- NEW `_timestamp_spacer.py` · spread 2h gap intra-día · 3 max/día · overflow día siguiente
- Atomic batch insert (todos o ninguno)
- Modal preview muestra timestamps calculados antes de confirmar

### 2.7 Video Polling Cancel (DEBT-CL-010 · opción B+a)

- NEW DELETE `/api/v1/content-lab/generate-video/{job_id}` · idempotente
- Frontend useRef cancelRef + cancel() callback
- Botón X "Cancelar" en placeholder pending video
- useEffect cleanup auto-cancela al unmount (zombie polling cerrado)
- Cierra agujero económico Veo ($2-10 por video evitado)

### 2.8 Calendar Auth Completa (DEBT-CL-013 · opción C)

- 4 endpoints `/api/v1/calendar/*` (POST/GET/PATCH/DELETE) ahora con auth + RBAC
- NEW `calendar/_access.py` helpers (resolve_client/account/post_or_403)
- Cerró agujero seguridad pre-existente · cualquiera podía agendar/listar/editar/eliminar posts ajenos

---

## 3 · BUGS LATENTES CERRADOS OPORTUNISTAS

| Bug | Detectado durante | Commit |
|-----|-------------------|--------|
| `ORDER BY is_primary` en calendar/_access · col inexistente schema V3 | DEBT-CL-015 dev | `9ce37d1` |
| `result.ok` en upgrade_aria.py · BillingResult es TypedDict no dataclass | DEBT-VID-001 dev | `6825e84` |
| `handleSubmit` sin onInvalid · zod errors silenciados | Bug Wizard Guardar | `cac7e21` |
| `web_search_tool` retorna `content` · backend research esperaba `snippet` | Bug 500 Brave | `aff6ecf` |
| Stripe SDK `StripeObject.metadata` no es dict puro · `.get()` colisión | Script Video Packs run | (local · ver sec 6.1) |

---

## 4 · ACCIONES MANUALES PENDIENTES OWNER

### 4.1 CRÍTICO · aplicar migraciones SQL

```bash
cd "D:/Omega Master redes"
supabase db push --linked   # aplica 00020 (media_url) + 00021 (uploaded_context_*)
```

Sin esto:
- `POST /calendar-v3/schedule/` → 500 (col media_url no existe)
- `POST /clients/{id}/upload-context` → 500 (cols uploaded_context_* no existen)

### 4.2 Stripe Video Pack env vars en Railway

Estado: ✅ ya pegadas según owner. Verificar que están activas:

```
STRIPE_PRICE_VIDEO_PACK_STARTER=price_1TaVSsGv6r9UZ1Dre2mQgz7U
STRIPE_PRICE_VIDEO_PACK_CREATOR=price_1TaVStGv6r9UZ1DrE3R7u41n
STRIPE_PRICE_VIDEO_PACK_CINEMATIC_PRO=price_1TaVStGv6r9UZ1Drrz70HoEp
```

Sin estas: `/billing/checkout-video-pack` retorna 503 `price_not_configured`.

### 4.3 Rotar STRIPE_SECRET_KEY (opcional · ya planeado)

Owner anunció rotación · `sk_test_xxx` actual queda en su poder. Cuando rote:
- Actualizar `STRIPE_SECRET_KEY` en Railway env var
- Webhooks Stripe siguen apuntando al mismo endpoint (no requieren cambio)

### 4.4 Verificar BRAVE_API_KEY en Railway

Estado: ✅ confirmado por owner. Si falla `/content-lab/research`:
- Backend retorna 503 `brave_not_configured` gracefully
- Toast frontend: "Brave Search no configurado"

### 4.5 Verificar Vercel auto-deploy

Cada `git push` debería triggerear Vercel build (~2 min). Si UI muestra código viejo:
- Vercel Dashboard → tu proyecto → Deployments → "Redeploy" el último commit

### 4.6 Smoke tests post-deploy

| Feature | Smoke esperado |
|---------|----------------|
| Aspect ratio 9:16 | Generar imagen `Story 9:16` → dimensiones 1024x1792 reales |
| Wizard Guardar | Editar cliente · modificar industry · Guardar Cambios · cerrar/reabrir · industry actualizado |
| Cancel video mid-flight | Generar video · click X durante polling · placeholder desaparece + row `video_generation_jobs.status='cancelled'` |
| Multi-client picker | Cliente con 2+ cuentas IG → dropdown "Cuenta" aparece · elegir → posts agendados con esa account |
| PDF attachment per-request | Adjuntar PDF en /content-lab + generar caption → backend log muestra `CONTEXTO ADJUNTO DEL CLIENTE` en system prompt |
| Upload context permanent | Subir context.md en wizard step 10 (editar cliente) → generar caption → system prompt incluye `CONTEXTO PERMANENTE DEL CLIENTE` |
| Brave Search cards | Input query Research · click verde → 5 cards azules en grid · "Usar snippet" appendea al topic |
| Video Pack checkout | `/add-ons` → click "Activar Pack" Starter siendo Pro → redirect Stripe Checkout test → pagar 4242 4242 4242 4242 → webhook → `client_plans.addons` jsonb +entry |
| Bulk schedule | Bloque con 3 captions + 1 imagen → agendar 25/5 10:00 → 3 rows en scheduled_posts con timestamps 10:00, 12:00, 14:00 |
| Wizard Guardar bugfix | Si zod falla, ahora toast destructive con detail visible (antes era silencioso) |

---

## 5 · DEBTs PENDIENTES (Sprint 4+)

### 5.1 Schema drift (alta prioridad)

- **DEBT-031 partial** · path write V3 cerrado (DEBT-CL-017) · read legacy aún broken
  · `scheduled_posts` legacy handler usa cols inexistentes
  · Refactor recomendado: migrar resto del calendar legacy a calendar_v3 o eliminar

### 5.2 OAuth flows social platforms (DEBT-040)

- Meta Business + Instagram + Facebook + TikTok + LinkedIn + YouTube
- Estimado: 40h
- Crítico para ARIA auto-publicar
- Tokens encrypted at rest en `social_accounts` table (cols ya existen)

### 5.3 ARIA Premium reseller variant (DEBT-046)

- Estimado: 4h
- Migration: `resellers.addons` jsonb
- `_resolve_role` para reseller dynamic aria_level
- Stripe product `aria_premium_reseller` $25/mes (ya en plan_pricing.py)

### 5.4 Persistent jobstore APScheduler (DEBT-047)

- Estimado: 4h
- Bloqueado por Python 3.13 + SQLAlchemy 2.0.25 incompat
- Opciones: bump SQLAlchemy O pin Python 3.11/3.12 en Railway

### 5.5 ARIA attention-based memory (DEBT-048)

- Estimado: 16h · sesión dedicada
- Voyage AI embeddings (nueva I1 excepción)
- pgvector RPC find_similar_memories ya existe
- Hoy ARIA memory recall es cronológico (últimos N) · spec dice attention-based

### 5.6 DEBT-029 partial · 33 `os.getenv` directos

- Migrar a `settings.xxx` (config layer único)
- Refactor por bounded context · Fase 3

### 5.7 Schema legacy frontend (DEBT-014/017 grace)

- 11+ frontend files >100L · 163 backend files >100L
- Grace period Fase 2 lift&shift
- Split progresivo Fase 3

### 5.8 DEBT-039 V1 (auto-populate wizard desde PDF)

- V2 cerrado (upload context al system prompt)
- V1 original: PDF brand guide → pypdf + Haiku → auto-popula `client_context` (niche/vertical/business_what/audience/tone)
- Estimado: 12h

### 5.9 DEBT-042 (regions display)

- Backend retorna `region: "PR,USA"` string single col
- Frontend wizard captura `regions: list[str]`
- ProfileSection muestra string crudo en lugar de chips
- Estimado: 3h · 2 opciones (migración a regions text[] o parse en componente)

---

## 6 · NOTAS TÉCNICAS · CAMBIOS LOCALES NO COMMITEADOS

### 6.1 Script Stripe `create_stripe_video_packs.py`

El script ya está en `main` (commit `b8e2811`). PERO tiene 3 fixes locales NO commiteados aplicados durante el run real:
1. Removido `from dotenv import load_dotenv` + `load_dotenv()` (owner pidió no dotenv · env var directo)
2. Bug Stripe SDK `(p.metadata or {}).get(...)` → try/except defensivo
3. Bug Stripe SDK `dict(p.metadata)` → acceso `p["metadata"]["key"]` con try/except

**Decisión owner pendiente**: ¿commitear los 2 SDK fixes (sin tocar el cambio dotenv) para que el script quede usable en el repo? O dejar todo local.

Status actual del archivo local · funcional · usado exitosamente.

---

## 7 · COMMITS DEL SPRINT 3 (orden cronológico)

```
a3dbb7c · docs(business): video pricing aprobado 23 may · packs S/C/CP
8132628 · feat(billing/domain): video entitlements por plan + add-on packs
1aba7be · feat(ui/addons): modal informativo Video Packs · pre-Stripe
d6b9a52 · feat(content-lab/ui): cablear VideoAddonModal cuando type=video
fd1f0fe · docs(sot): DEBT-VID-001 + hito Sprint 3 Video Pricing arranque
1132124 · feat(add-ons): página dedicada /add-ons con Video Packs
8a64227 · refactor(content-lab): link a /add-ons en vez de modal
c691341 · fix(content-lab/ui): pulso ámbar en botón Video Packs
ba74667 · UX-1 fix isPending cableado
7318b13 · UX-4 variation checkboxes compactos
8dbbad8 · UX-3 aspect ratio · cierra DEBT-CL-008/009
4bf3bd2 · UX-6 upload imagen referencia
4345fdd · UX-2 botón ✨ Mejorar Prompt vía Claude Haiku
d391708 · fix paperclip dentro textarea · variations y aspect 2 líneas
8cc3112 · fix paperclip siempre visible · DEBT-CL-020 register
04567ac · fix(clients/models): sanear ClientProfile · cierra DEBT-CL-016
0f36425 · fix(content-lab): backend respeta client_id frontend · DEBT-CL-005
769d362 · docs(sot): DEBT-CL-005 marcada CERRADA
2d36666 · fix(clients/onboarding): required_insert para writes críticos
3a504ec · fix(nano-banana): re-habilitar ImageConfig · cierra DEBT-CL-011
91d99a8 · fix(calendar): auth + RBAC en 4 endpoints · cierra DEBT-CL-013 (C)
d300117 · feat(calendar-v3): NEW POST /schedule · cierra DEBT-CL-017
dcf9389 · docs(sot): DEBT-CL-017 marcada CERRADA
155d4ae · feat(calendar-v3): bulk schedule N posts · cierra DEBT-CL-018
9ce37d1 · feat(content-lab): multi-account picker + fix is_primary · DEBT-CL-015
891315f · feat(brand-dna): industry defaults fallback · DEBT-CL-019
bb3257b · docs(sot): DEBT-CL-012 verificada OK
86599d8 · feat(video): cancelable polling + backend cancel · DEBT-CL-010
c2d4a03 · refactor(aria): consolidar auth helpers · cierra DEBT-CL-003
7603929 · feat(content-lab): PDF/DOCX/MD/TXT attachment · DEBT-CL-020
6825e84 · feat(billing): Stripe Video Pack Checkout · DEBT-VID-001
af1dfcd · refactor(auth): consolidar 4 helpers fuera cluster ARIA · DEBT-CL-021+022
b34ba23 · docs(pendientes): DEBT-CL-021/022 marcadas CERRADAS
24afe0b · feat(content-lab): Brave Search cableado · botón Research vivo
db3aa58 · refactor(content-lab): research como cards en grid · UX rework
aff6ecf · fix(content-lab/research): mapear content→snippet · cierra 500
b8e2811 · chore: scrollbar textarea + script Stripe Video Packs
2dd5eb4 · feat(clients): upload context doc · injection system prompt RAFA
cac7e21 · fix(onboarding): handleSubmit onInvalid · cierra silenciamiento zod
```

---

## 8 · ESTADO DEL SISTEMA · 24 may 2026 01:50 AST

**Backend Railway** · `omega-production-3c67.up.railway.app` · operativo · pre-push 10/10 verde en cada commit.

**Frontend Vercel** · `omegaraisen.agency` · auto-deploy esperado tras cada push (verificar Dashboard si demora).

**Database Supabase** · 19 migraciones aplicadas (después de owner correr `db push --linked` · serán 21).

**Stripe test mode** · 3 productos Video Pack + price_ids cargados en Railway env vars.

**Token cost trend** (per generación):
- Caption text · ~$0.001-0.005 (Sonnet 4.6 default)
- Caption con attachment per-request (CL-020) · +$0.01-0.05 (50K chars context)
- Caption con upload context permanent (V2) · +$0.01-0.05 (50K chars context · CADA generación)
- Image · ~$0.04 (Nano Banana)
- Video 8s/30s/60s · ~$2/$5/$10 (Veo 3.1)

---

## 9 · PRÓXIMA SESIÓN · RECOMENDACIÓN DE ORDEN

Owner decide. Sugerencias por prioridad:

1. **Aplicar migraciones SQL + smoke tests** (acción manual · 30 min)
2. **DEBT-CL-022 GenerateContentSheet cliente real** (verificar end-to-end · 15 min)
3. **DEBT-039 V1** · auto-populate wizard desde PDF (12h · UX premium)
4. **DEBT-040 OAuth flows** (40h · crítico para auto-publish · Sprint dedicado)
5. **DEBT-046 ARIA Premium reseller** (4h · revenue stream)
6. **DEBT-048 ARIA attention memory** (16h · diferenciador competitivo)
7. **DEBT-031 read legacy** (refactor calendar listing al schema V3 · ~6h)

Mientras tanto: **Brave + Video Packs + Upload Context** son flow productivo end-to-end completo para clientes reales.

---

## 10 · SESIÓN 24 MAY · CIERRE COMPLETO (4A + 4B + BUGs + auto-search)

### Estado por bloque
```
SPRINT 4A
  4A-1 ✅  subagente guardian (gate) + 4 builders dev-tooling
  4A-2 ⏸   outcome_evaluator — PAUSADO (no hay señal de outcome real aún)
  4A-3 ✅  input_sanitizer + 5 consumidores cableados
  4A-4 ✅  DEBT-002 analytics sin datos sintéticos (banner honesto + CTA)
  4A-5 ✅  config fail-secure (environment=production · debug=False)
SPRINT 4B — GUARDIAN (seguridad usuario/sesión)
  4B-1 ✅  migración 00022 (3 tablas + RLS + is_owner)
  4B-2 ✅  analyzer heurístico + repo + tests
  4B-3 ✅  trigger login + /guardian/login-event + /guardian/session-report
  4B-4 ✅  SecurityKPICard (cliente)
  4B-5 ✅  SentinelDashboardCard (superadmin) + /sentinel/status asegurado
BUGS ARIA
  BUG 1 ✅  contexto subido reaparece al reabrir wizard
  BUG 2 ✅  ARIA lee el contexto real del cliente (cap 1500)
FEATURE
  Auto-Brave-Search ✅  ARIA + Content Lab (buscan info actual · snippets saneados T2)
```
Detalle + hashes: `SOURCE_OF_TRUTH.md` §11/§12/§13. Specs gitignored: `PROTOCOLO_SEGURIDAD_INPUT_OMEGA.md`, `GUARDIAN_SECURITY_AGENT.md`.

### 🔴 ACCIÓN MANUAL CRÍTICA DEL OWNER (bloquea features en prod)
```bash
cd "D:/Omega Master redes"
supabase db push --linked
```
Aplica migraciones **00020 · 00021 · 00022** (aún sin correr contra el Supabase real).
**Sin esto, en producción:**
- `/clients/{id}/upload-context` → 500 (col `uploaded_context_text` no existe) → BUG 1/2 y ARIA-contexto NO funcionan.
- `/guardian/*` y `SecurityKPICard`/`SentinelDashboardCard` → 500/empty (tablas 00022 no existen).
- `/calendar-v3/schedule/` media_url → 500 (00020).
El código + tests están verdes; **solo falta el deploy de migración.** Verificar luego que las tablas tengan RLS=true.

### Pendientes técnicos (Sprint 5+)
- **4A-2 outcome_evaluator** — esperando una señal de outcome real (sin ella, evaluaría a ciegas · viola P1).
- **Capa 2 Haiku** del input_sanitizer + del GUARDIAN analyzer (anti-falsos-positivos · con volumen real).
- **DEBT abiertas previas:** 040 (OAuth social), 046 (ARIA Premium reseller), 047 (jobstore Py3.13), 048 (ARIA attention memory · embeddings), 031 (calendar read legacy), 042 (regions display), 039 V1 (auto-populate wizard desde PDF).
- **/sentinel/* restantes** (scan/history/deploy-check) siguen SIN auth — hallazgo pre-existente (solo /status asegurado en 4B-5).
- **`/guardian/login-event`** es señal complementaria (un cliente autenticado podría reportar success arbitrario) · la fuente de verdad server-side es `auth/login.py`.
- **brute_force path Supabase**: fallos client-side no llegan al backend (sin JWT) · legacy cubre server-side.
- **`scripts/create_stripe_video_packs.py`**: fixes locales sin commitear (decisión owner pendiente · §6.1).

### Próxima sesión — recomendación
1. Correr `supabase db push --linked` + smoke de GUARDIAN/ARIA-contexto/auto-search contra DB real.
2. Decidir Sprint 5 scope (Capa 2 Haiku · 4A-2 si hay señal · DEBTs 040/046).

---

> **→ Sesión siguiente (25 may):** AUDIT 1/2 wizard% + picker · BUG A persistencia · seguridad
> role server-side · hard delete · wizard 3 fixes · logo overlay · ARIA regiones + X/10 · DEBT-049.
> Detalle: **`PENDIENTES_Y_PROGRESOS_20260525.md`** + **`SOURCE_OF_TRUTH.md` §14**.

```
PENDIENTES_Y_PROGRESOS_20260524.md
Sesión 24 may · 4A (5) + 4B (5) + BUG 1/2 + auto-Brave-Search · ~30 commits · gate 10/10 c/u · 0 downtime
Firmado: Claude Opus 4.7 (1M context) + Ibrain Raisen (CEO)
🐢💎 No velocity. Only precision.
```
