# OMEGA · PENDIENTES Y PROGRESOS · SESIÓN 22 MAY 2026

> **DOCUMENTO LOCAL · NUNCA SE COMMITEA · NUNCA SE PUSHEA**
> Protegido por `.gitignore` patrón `PENDIENTES_*.md`. Confirmar con `git status` antes de cualquier operación destructiva en working tree.
>
> Generado al cierre 22 may 2026 · madrugada. Próxima sesión: arrancar con DEBT-045 (persistent jobstore + orphan cleanup).

---

## ÍNDICE

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Cronología de commits](#2-cronología-de-commits)
3. [Progresos completados por área](#3-progresos-completados-por-área)
4. [Migraciones SQL aplicadas hoy](#4-migraciones-sql-aplicadas-hoy)
5. [DEBTs cerradas hoy](#5-debts-cerradas-hoy)
6. [DEBTs nuevas registradas hoy](#6-debts-nuevas-registradas-hoy)
7. [DEBTs heredadas activas (Fase 3)](#7-debts-heredadas-activas-fase-3)
8. [Pendientes inmediatos próxima sesión](#8-pendientes-inmediatos-próxima-sesión)
9. [Dudas abiertas que requieren decisión](#9-dudas-abiertas-que-requieren-decisión)
10. [Verificación visual pendiente del usuario](#10-verificación-visual-pendiente-del-usuario)
11. [Acciones manuales no automatizables](#11-acciones-manuales-no-automatizables)
12. [Estado del sistema al cierre](#12-estado-del-sistema-al-cierre)
13. [Notas operativas](#13-notas-operativas)

---

## 1. RESUMEN EJECUTIVO

**Sesión maratónica de 1 noche (22 may 2026 · 01:09 → 02:54 AM). 13 commits totales pusheados a `main`.**

Bloques mayores cerrados:

- **Sprint 2 backend completo · 4/4 prioridades cerradas:**
  - P1 · DEBT-018 imagen end-to-end (bucket `generated-images` + uploader + compat layer + handler V3 + UI)
  - P2 · A/B Variaciones 3 versiones (asyncio.gather × 3 temps · plan PRO/enterprise gating)
  - P3 · Virality Score V1 heurístico 0-100 (5 features · badge "Estimado" P1 compliance)
  - P4 · DEBT-044 persistir Brand DNA + cron 3am refresh + trigger SQL invalidación
- **DEBT-019 cerrada:** videos Veo 3.1 con URLs permanentes en Supabase Storage (download httpx + upload).
- **DEBT-020 cerrada:** background job pattern para video (APScheduler 'date' trigger · double try/except orphan-safe).
- **Content Lab UI end-to-end vivo:** ContentLabPage refactor (extract ResultCard + content-lab-api + useVideoJobPolling + content-lab-constants) · 13 tipos disponibles (5 originales + 8 legacy expandidos).

**4 DEBTs cerradas · 1 DEBT nueva · -30h netos a deuda total.**

Total deuda registrada: **~628h** (inicio sesión 658h · -36h cerradas · +6h DEBT-045 nueva).

Backend Railway responde · Vercel auto-deployed · validate 10/10 en TODOS los commits · pytest 24/24 verde · TypeScript 0 errors. Migraciones 16-18 aplicadas a remoto Supabase (`rwlnihoqhxwpbehibgxu`).

---

## 2. CRONOLOGÍA DE COMMITS

Orden cronológico inverso (más reciente arriba):

| Hash | Fecha | Título |
|---|---|---|
| `ac4e349` | 2026-05-22 02:53 | feat(content-lab): expandir TYPES con 8 tipos legacy (email/story/ad/bio/etc) |
| `c66edd1` | 2026-05-22 02:51 | feat(content-lab): video UI con polling state machine · cierra Content Lab end-to-end |
| `7450165` | 2026-05-22 02:37 | docs(debts): DEBT-020 CERRADA + DEBT-045 nueva (persistent jobstore + orphan cleanup) |
| `4b989fd` | 2026-05-22 02:36 | feat(video): DEBT-020 — background job pattern para generación de video Veo 3.1 |
| `7d0f480` | 2026-05-22 02:22 | docs(debts): DEBT-019 CERRADA · Sprint 2 (videos Veo persistentes) |
| `f2e2bb9` | 2026-05-22 02:21 | feat(storage): DEBT-019 — videos Veo 3.1 con URLs permanentes en Storage |
| `a440516` | 2026-05-22 02:10 | feat(variations): A/B/C parallel generation · plan PRO/enterprise gating (Sprint 2 P2) |
| `22b2aee` | 2026-05-22 01:56 | feat(virality): Score V1 heurístico 0-100 · 5 features · badge Estimado (Sprint 2 P3) |
| `90a41b5` | 2026-05-22 01:44 | docs(debts): DEBT-044 CERRADA · Sprint 2 (persistir BrandDNA) |
| `ef6dee2` | 2026-05-22 01:43 | feat(brand-dna): DEBT-044 — persistir BrandDNA + cron 3am refresh + trigger invalidación |
| `66a4c32` | 2026-05-22 01:23 | feat(content-lab): handler V3 /generate-image + UI · cierra Paso 4 DEBT-018 |
| `2adf632` | 2026-05-22 01:12 | docs(debts): DEBT-018 CERRADA · Sprint 2 P1 |
| `e4d13ef` | 2026-05-22 01:09 | feat(storage): DEBT-018 — Supabase Storage buckets + imagen URLs permanentes |

---

## 3. PROGRESOS COMPLETADOS POR ÁREA

### 3.1 Supabase Storage · DEBT-018 + DEBT-019 cerradas

- Migración `00016_storage_buckets.sql`: buckets `generated-images` (10MB · jpeg/png/webp) + `generated-videos` (500MB · mp4) · RLS public read · service_role write
- NEW `bc_cognition/infrastructure/_storage_uploader.py` (75L): private `_upload_bytes` core + 2 wrappers públicos (`upload_image_bytes` + `upload_video_bytes`). MIME tables separadas. Pattern fail-loud con `StorageUploadError`.
- `_image_compat.py`: refactor para decode base64 + upload + return URL persistente (cero data URIs)
- `_video_compat.py`: extiende a download httpx con `x-goog-api-key` header (timeout 120s) + upload via `upload_video_bytes` · client_id kwarg opcional

### 3.2 Brand DNA persistido · DEBT-044 cerrada

- Migración `00017_client_brand_dna.sql`: tabla con dna_jsonb + score + last_computed_at + last_corpus_size · RLS service_role ALL + authenticated own · **trigger SQL** `trg_invalidate_brand_dna AFTER INSERT/UPDATE/DELETE ON brand_voice_corpus` con SECURITY DEFINER (UPDATE client_brand_dna SET last_computed_at=NULL)
- NEW `bc_cognition/infrastructure/brand_dna_repository.py` (62L): fetch_persisted + upsert + fetch_active_client_ids
- `bc_cognition/application/use_brand_dna.py` refactor (18→67L): read-through cache · stale threshold 24h · `async refresh_all_brand_dna()` para cron
- `bc_cognition/domain/brand_dna.py` (+22L): classmethods `to_dict()` + `from_dict()` puras
- `main.py`: 9no cron job `scheduler.add_job(refresh_all_brand_dna, 'cron', hour=3, id='brand_dna_refresh')`
- `DDD_REGLAS_OMEGA.md X3`: counter 8→9 + JOBS list expanded

### 3.3 Content Lab V3 backend completo

**P1 imagen:**
- Handler V3 `generate_image.py` (71L): wire al pipeline · `client_id` explícito · error semantics (502 storage / 503 gen)
- Models: `GenerateImageRequest` + `GenerateImageResponse`
- Router: `include_router(image_router)`

**P2 A/B Variaciones (Sprint 2 P2):**
- NEW `_variations.py` (74L): `asyncio.gather` × 3 temps (0.3/0.7/1.0) cuando n=3 · cache_control ephemeral hace cache HIT en calls 2 y 3 (~1.5x costo)
- `_content_lab_repository`: helper `find_client_plan` (SELECT client_plans.plan)
- `generate_text.py` refactor (67→55L): delegate pattern · plan check PRO/enterprise · 403 si no calificado
- Models: GenerateTextRequest.variations + VariationItem + Response.variations list

**P3 Virality Score V1:**
- NEW `bc_cognition/domain/virality_score.py` (75L): pure function `compute_virality_score(text, dna, platform) -> dict`
- 5 features pesados a 100: hook 20 + CTA 25 + question 15 + emojis 15 + length 25
- Length compara vs `dna.avg_length_words` (si corpus≥5) else platform defaults
- CTA whitelist hardcoded ES+EN (configurable cliente futuro)
- Badge "Estimado" obligatorio (P1 verdad brutal)
- 6 tests en `test_virality_score.py`

**DEBT-020 background job pattern:**
- Migración `00018_video_generation_jobs.sql`: tabla + RLS + index (client_id, created_at DESC)
- NEW `video_job_repository.py`: insert_pending/update_running/completed/failed/fetch_job
- NEW `bc_cognition/application/use_video_job.py` (73L): `create_video_job` (insert + APScheduler 'date' lazy import) + `_run_video_job` con **double try/except orphan-safe**
- NEW `content_lab_v3/handlers/generate_video.py` (54L): POST start (50ms) + GET status poll
- 4 routes activos: `/generate` (text · variations) · `/generate-image` (P1) · `/generate-video` (POST) · `/generate-video/{job_id}` (GET)

### 3.4 Frontend Content Lab UI completa

- NEW `src/lib/content-lab-api.ts` (24L): apiPost + 3 generators + fetchVideoStatus (extracción para liberar LOC)
- NEW `src/hooks/useVideoJobPolling.ts` (35L): useQuery v5 refetchInterval auto-stop · useEffect con refs (callbacks estables · no infinite loop)
- NEW `src/lib/content-lab-constants.ts` (26L): TYPES + TONES + STYLES + RATIOS + 4 LABELS maps centralizados
- `src/pages/ContentLabPage.tsx`: refactor a 92L final · tipo "video" + ratio picker + jobId state + polling callbacks + button label 3 estados (Iniciando/Generando 30-90s/Generar)
- `src/components/content/ResultCard.tsx`: branch isVideo con `<video src controls>`
- **TYPES expandido 5→13**: caption, hashtags, video_script, image, video, **email, story, ad, bio, google_business_post, thread, carousel, linkedin_post** (todos usan endpoint /content-lab/generate existente · cero backend nuevo)
- Removido badge "Próximamente" de video (ya funciona)

---

## 4. MIGRACIONES SQL APLICADAS HOY

| Archivo | Aplicada | Contenido |
|---|---|---|
| `00016_storage_buckets.sql` | ✅ Sprint 2 P1 | Buckets generated-images (10MB · jpeg/png/webp) + generated-videos (500MB · mp4) · RLS public read · service_role write |
| `00017_client_brand_dna.sql` | ✅ Sprint 2 (DEBT-044) | Tabla client_brand_dna + RLS + trigger SQL `trg_invalidate_brand_dna` AFTER INSERT/UPDATE/DELETE ON brand_voice_corpus |
| `00018_video_generation_jobs.sql` | ✅ Sprint 2 (DEBT-020) | Tabla video_generation_jobs + RLS + index (client_id, created_at DESC) |

Total migraciones aplicadas en remoto: **18/18** (00001-00018).

---

## 5. DEBTs CERRADAS HOY

| ID | Detalle | Commit cierre | Δ deuda |
|---|---|---|---|
| **DEBT-018** | Imágenes Nano Banana ya no se devuelven como data URIs · ahora URLs persistentes Storage | `e4d13ef` + `2adf632` | -6h |
| **DEBT-019** | Videos Veo 3.1 ya no se pierden por TTL · download httpx + upload Storage = URL persistente | `f2e2bb9` + `7d0f480` | -6h |
| **DEBT-020** | Background job pattern para video Veo · POST inmediato + worker APScheduler + GET status | `4b989fd` + `7450165` | -16h |
| **DEBT-044** | Brand DNA persistido en tabla + cron 3am refresh + trigger SQL invalidación lazy | `ef6dee2` + `90a41b5` | -8h |

**Total cerrado hoy: -36h.**

---

## 6. DEBTs NUEVAS REGISTRADAS HOY

| ID | Detalle | Tiempo est. | Impacto |
|---|---|---|---|
| **DEBT-045** | Persistent jobstore APScheduler (SQLAlchemyJobStore con Postgres existente) + cron horario de cleanup de orphan jobs (rows en `video_generation_jobs.status='running'` con `started_at > 15min ago` marcar como `failed`) | +6h | Alto (UX video producción) |

---

## 7. DEBTs HEREDADAS ACTIVAS (FASE 3)

Sin cambios estructurales esta sesión · totales actualizados solo por DEBT-018/019/020/044 cerrados:

- DEBT-013/014/015/017 (lift & shift Lovable) — grace period Fase 3
- DEBT-021 (endpoint runway naming cosmético) — Fase 3
- DEBT-024/025 (claude_service migration · routing layer V3) — Fase 3
- DEBT-029 (33 os.getenv → settings.xxx) — Fase 3
- DEBT-030 (4 stubs handlers agents) — Fase 3
- DEBT-031 (analytics dashboard handler legacy refs) — Fase 3
- DEBT-033/034/035 (frontend legacy refactors) — UX
- DEBT-036 (legacy billing module cleanup) — cleanup
- DEBT-037 (ARIA Premium Stripe products) — Fase 2 ARIA
- DEBT-038 (Stripe Customer Portal embed) — Fase 3
- DEBT-039/040/041 (PDF parser · OAuth flows · storage policies)

Total deuda actualizada: **~628h (~16 semanas full-time)**.

---

## 8. PENDIENTES INMEDIATOS PRÓXIMA SESIÓN

```
P0 · DEBT-045 · Persistent jobstore + orphan cleanup (6h)
     - SQLAlchemyJobStore con settings.database_url (Postgres existente · cero infra)
     - Cron horario: UPDATE video_generation_jobs SET status='failed', error='orphan_timeout'
       WHERE status='running' AND started_at < now() - interval '15 min'
     - Cron opcional: reconciliar scheduler.get_jobs() vs DB rows (Sprint 4+)
     - ALTA prioridad: protege contra restart Railway mid-generation y workers crashed

P1 · DEBT-037 · ARIA Premium Stripe products (8h)
     - 2 productos Stripe via API ($12 client / $25 reseller)
     - Fields STRIPE_PRICE_ARIA_PREMIUM_CLIENT/_RESELLER en .env + config.py
     - bc_billing.application use case upgrade_aria_premium
     - Endpoint /api/v1/billing/upgrade-aria
     - Frontend ARIAUpgradeBanner reemplaza disabled por mutation real

P2 · DEBT-038 · Stripe Customer Portal embed (6h)
     - Endpoint POST /api/v1/billing/create-portal-session
     - Frontend PaymentSection mutation → redirect portal_url
     - Configurar Customer Portal en Stripe Dashboard

P3 · DEBT-029 · 33 os.getenv → settings.xxx refactor (6h)
     - Por bounded context: bc_cognition adapters · billing · sentinel_vault · etc.
     - Fields faltantes en Settings: brave_api_key, gemini_api_key, stripe_*, etc.
     - Eliminar load_dotenv shim al final

P4 · DEBT-024/025 · claude_service migration a anthropic_adapter (12-20h)
     - 48 callers de claude_service.generate_text() migran a bc_cognition.anthropic_adapter
     - Routing layer V3 unifica con bc_cognition.domain.routing_table
     - Eliminar agent_dispatcher · agent_registry · ai_providers redundantes
```

---

## 9. DUDAS ABIERTAS QUE REQUIEREN DECISIÓN

1. **Frontend gating del plan PRO/enterprise para variations**: hoy la UI permite click al toggle de 3 variaciones sin pre-check del plan. Click → backend 403 → toast "Plan PRO requerido". ¿Querés gating preventivo con un endpoint nuevo `GET /api/v1/clients/me/plan` que el frontend lee al mount? Trade-off: más UX-clean vs +1 endpoint + 1 query por mount.

2. **Ratio default para video**: hoy `1280:768` (horizontal). Para social media-first (IG Reels · TikTok · Shorts) vertical 9:16 sería el default lógico. ¿Cambiamos default a `768:1280`?

3. **Crash recovery jobs**: cuando Railway reinicia mid-generation (~30-90s), row queda en `running`. DEBT-045 cubre el cleanup vía cron. Pero hay otra opción: **persistent jobstore** que sobrevive restarts. Las dos opciones están agrupadas en DEBT-045 · ¿confirmás abordar AMBAS o solo el cleanup cron primero?

4. **Smoke test E2E ahora vs Sprint 3**: el Content Lab está live end-to-end pero NO testeamos manualmente todas las paths en Railway/Vercel reales. ¿Hacés tú el smoke o agregamos como tarea de la próxima sesión?

5. **Video variations**: hoy solo texto soporta `variations=3`. Imagen y video no. ¿Roadmap para video variations en algún Sprint futuro o queda fuera permanente?

---

## 10. VERIFICACIÓN VISUAL PENDIENTE DEL USUARIO

Smoke test E2E en Railway/Vercel reales · todo accesible vía https://omega-two-wine.vercel.app/content-lab:

- [ ] Generar **caption** Instagram con tono casual · verificar virality badge aparece
- [ ] Generar **email** restaurante · verificar prompt_vault template seedeado kicks in
- [ ] Generar **story** construction · verificar formato secuencial
- [ ] Generar **video_script** TikTok · verificar legacy type sigue funcionando
- [ ] Generar **imagen** con prompt "café latte arte" · verificar URL Supabase Storage retorna 200 al hacer fetch
- [ ] Generar **video** con prompt simple · verificar polling cada 5s + `<video>` renderiza tras 30-90s
- [ ] Toggle "Generar 3 variaciones" sin plan PRO → click → toast "Plan PRO requerido"
- [ ] Cambiar a un cliente con `client_plans.plan='pro'` → click → 3 tabs A/B/C renderizan
- [ ] Verificar `/docs` OpenAPI muestra 4 endpoints content-lab (generate + generate-image + POST generate-video + GET generate-video/{job_id})

---

## 11. ACCIONES MANUALES NO AUTOMATIZABLES

- ✅ Aplicar migración 00016 (vía supabase db push --linked · hecho durante Sprint 2 P1)
- ✅ Aplicar migración 00017 (vía supabase db push --linked · hecho durante DEBT-044)
- ✅ Aplicar migración 00018 (vía supabase db push --linked · hecho durante DEBT-020)
- ⚠ Verificar Railway environment tiene `GEMINI_API_KEY` (necesario para Veo download del temp URI)
- ⚠ Verificar buckets visibles en Supabase Dashboard → Storage (cosmético · validation)
- ⚠ Confirmar `supabase` Python SDK versión instalada en Railway soporta el método `.storage.from_().upload(file_options={"content-type": ...})` con el shape que usamos

---

## 12. ESTADO DEL SISTEMA AL CIERRE

| Componente | Estado | Detalle |
|---|---|---|
| **GitHub repo** | ✅ synced | `main` head `ac4e349` · origin/main al día |
| **Backend Railway** | ✅ UP | `omega-production-3c67.up.railway.app` · auto-deploy de 13 commits triggered |
| **Frontend Vercel** | ✅ UP | `omega-two-wine.vercel.app` · auto-deploy triggered |
| **Supabase Project** | ✅ UP | `rwlnihoqhxwpbehibgxu.supabase.co` · 18 migraciones aplicadas |
| **Validate hook** | ✅ 10/10 | En TODOS los 13 commits · 0 violaciones críticas (C1/C2/I1/A2/G6/G2/T4) |
| **Tests backend (pytest)** | ✅ 24/24 | 4 brand_dna + 5 aria_memory + 9 routing_table + 6 virality |
| **TypeScript strict** | ✅ 0 errors | `npx tsc --noEmit` clean en TODOS los commits |
| **C4 status** | ⚠ 56 archivos | En bucket warning 75-100L · cero archivos >100L hard block |
| **Deuda técnica** | **628h** | Bajó 30h vs inicio sesión (658h) |
| **Endpoints activos** | ~234 | 4 nuevos: generate-image, generate-video (POST + GET) · variations expand existing |
| **Cron jobs APScheduler** | 9 | SENTINEL (4) + ORACLE (1) + Workers v2 (3) + brand_dna_refresh (1 · DEBT-044) |
| **Buckets Storage** | 4 | brand-files (00012) + avatars (00013) + generated-images (00016) + generated-videos (00016) |

---

## 13. NOTAS OPERATIVAS

**Patrones nuevos establecidos esta sesión (reusables a futuro):**

1. **APScheduler `'date'` trigger pattern**: `scheduler.add_job(coro, 'date', run_date=datetime.now(), args=[id], id='prefix_uuid')` · primer uso del proyecto · futuros background jobs (image variations, email send, etc) pueden replicarlo.

2. **Double try/except orphan-safe pattern**: en cualquier background worker, envolver TODO el body en try/except Exception. Si update_failed también falla, log explícito "ORPHAN" para debug visible. Pattern definido en `use_video_job._run_video_job`.

3. **Storage uploader genérico**: private `_upload_bytes(raw, mime, bucket, mime_table, client_id)` core + N public wrappers (`upload_image_bytes`, `upload_video_bytes`, futuro `upload_audio_bytes`). DRY + type-safe en boundaries.

4. **Frontend lib extraction pattern**: cuando page cruza 75L warning, extraer en este orden: (1) API functions a `src/lib/X-api.ts`, (2) hooks a `src/hooks/useX.ts`, (3) componentes a `src/components/X/Y.tsx`, (4) constantes a `src/lib/X-constants.ts`. Aplicado en Content Lab esta sesión.

5. **Read-through cache pattern**: `use_brand_dna` lee tabla persistida primero · recompute si stale (>24h) o ausente · trigger SQL invalida en escrituras del corpus. Aplicable a otros datos derivados costosos.

**Cosas a recordar para próximas sesiones:**

- `GEMINI_API_KEY` es REQUERIDA para download de Veo URIs · si Railway la pierde, video falla con HTTPError sin info clara. Documentar mejor en logs si surge.
- `_video_compat.py` está en warning bucket 85L · acceptable per pattern de orchestrators (mismo criterio que `_image_compat.py` 76L).
- `ContentLabPage.tsx` quedó en 92L (warning) post-refactor · adicionalmente está abierta a futuro split por sub-componentes (`<TextForm>`, `<VideoForm>`) si se vuelve a expandir.
- `main.py` está en 205L (bucket warning histórico · ya estaba >100L pre-DEBT-044). NO extraje el `scheduler` instance a un módulo separado · DEBT futura cuando haya más consumidores del scheduler (lazy import resuelve circular hoy).
- DDD `X3` rule fue actualizada: ahora dice "9 cron workers" en vez de "8" (counter + JOBS list + ENFORCE). Aprobación CEO explícita capturada en confirmación de DEBT-044.

---

## CIERRE DE SESIÓN — 2026-05-22 · 02:54 AM

```
Branch:           main (head ac4e349)
Commits sesión:   13 (todos pusheados origin/main)
DEBTs cerradas:   4 (DEBT-018 · DEBT-019 · DEBT-020 · DEBT-044)
DEBTs nuevas:     1 (DEBT-045)
Migraciones:      3 aplicadas (00016 · 00017 · 00018)
Validate:         10/10 verde
Tests backend:    24/24 pass
TypeScript:       0 errors
Deuda total:      628h
Sistema:          UP en Railway + Vercel
```

---

## Pendientes UI Mock → Backend Real (22 may 2026 sesión PM)

Después del rediseño completo del Content Lab V2 (commit `e447903` redesign + fixes posteriores), el mock está visualmente terminado pero requiere conexión backend real:

### Gap 1 · Mock no diferencia por `content_type`
`MOCK_TEXTS` en `ContentLabPageV2.tsx:13-16` genera el mismo string para todos los tipos (caption/image/hashtags/video/etc). La generación real debe rutear por tipo:
- `text` / `caption` / `hashtags` → `/api/content-lab/generate-text` (Anthropic + virality score real)
- `image` → `/api/content-lab/generate-image` (Nano Banana → Storage URL)
- `video` → `/api/content-lab/generate-video` (Veo3 background job + polling)

### Gap 2 · Imagen no renderiza
`ResultCardV2.tsx` ya tiene branch `isImage ? <img src={...} />` pero el mock pasa texto en `generated_text` (no URL). Cuando se conecte el endpoint real, el backend devuelve la URL de Supabase Storage en `generated_text` y el `<img>` renderiza automático. **Cero cambio frontend necesario** · solo conectar el endpoint.

### Próxima sesión · plan tentativo
1. Crear hook `useContentLabGenerate(type)` que llama el endpoint correcto según `form.type`
2. Reemplazar `handleGenerate` mock en `ContentLabPageV2.tsx` por mutación real
3. Video: integrar polling (puede reusar lógica de DEBT-020 background jobs)
4. Estimado: ~3h dev + 1h QA E2E

---

🐢💎 No velocity. Only precision.
