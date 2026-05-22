# PENDIENTES_Y_PROGRESOS · 21 mayo 2026

> Cierre de Sprint 1 · Content Lab corazón del sistema activado.
> 4 tareas · 4 commits · pusheados a main · Railway + Vercel auto-deployed.

---

## 1. Resumen ejecutivo del Sprint 1

Sprint 1 completo: **el Content Lab pasa de spec a pipeline real wireado en producción**. RAFA persona escrita en T2 deja de ser dead code en T3 cuando se enchufa al endpoint `/content/generate` enriquecido con Brand DNA del cliente. ARIA cierra el loop P5 en T4 leyendo memoria antes de cada respuesta. Cero breaking changes · validate 10/10 · 18/18 tests pass.

Branch local ahead 4 al cierre de T4 → push autorizado por owner → `cb444ae..8a6a415 main -> main` exitoso → auto-deploys Railway + Vercel disparados.

---

## 2. Commits del Sprint 1

```
8a6a415  feat(bc_cognition): ARIA lee agent_memory al inicio · close P5 loop (Sprint 1 T4)
6e1c442  feat(bc_cognition): Brand DNA Builder + wire RAFA al endpoint /content/generate (Sprint 1 T3)
c8639da  feat(bc_cognition): personas RAFA + ATLAS · content_creator + brand_voice system prompts
6497a83  feat(content-lab): seed prompt_vault 30 prompts + migración 00014/00015
```

---

## 3. Qué hace cada tarea (en palabras simples)

### Tarea 1 · `seed_prompt_vault` 30 prompts (commit 6497a83)

Creó la tabla `prompt_vault` en Supabase con migraciones 00014 (schema + RLS) + 00015 (campo `slot_name` para resolver 4 colisiones de tuples idénticos) y cargó los 30 prompts canónicos de RAFA que están documentados en `CONTENT_LAB_OMEGA_MASTER.md §5`. Cada prompt es un template parametrizable por categoría / vertical / plataforma (caption restaurant instagram, script construction reel, etc.). El seed script (`scripts/seed_prompt_vault.py`) es idempotente vía upsert: se puede re-correr sin duplicar.

### Tarea 2 · Personas RAFA + ATLAS (commit c8639da)

Escribió 2 system prompts inmutables en `bc_cognition/domain/personas/`:

- **RAFA** (`content_creator.py`, 75L): copywriter que genera todo el contenido de texto. 8 secciones: identidad, misión, principios P1-P5, cómo genera, fórmulas AIDA/PAS/BAB/storytelling, reglas por plataforma, hard rules, formato output JSON.
- **ATLAS** (`brand_voice.py`, 55L): guardián de marca que valida outputs de RAFA contra los 7 quality gates de OmegaRaisen. Retorna score 0-1 + verdict approve/revise/reject + sugerencia de fix.

**Cero breaking changes**: `persona_nova.py` (X2 SHA1 declarado) y `persona_aria.py` (paramétrico por nivel/rol · usado por `use_aria_message`) quedaron intactos. La nueva subcarpeta `personas/` coexiste con el patrón flat existente.

### Tarea 3 · Brand DNA Builder + wire RAFA (commit 6e1c442)

Implementó el Brand DNA Engine descrito en `CONTENT_LAB §6`. Pipeline completo:

- **Lectura corpus**: nuevo `brand_voice_corpus_repository.fetch_recent_corpus(client_id, limit=20)` con safe-fetch (Supabase down → `[]`, no rompe generación)
- **Builder puro**: `_brand_dna_builder.build_brand_dna(corpus)` → `BrandDNA(tone, keywords, avg_length_words, top_post_excerpts, corpus_size, score)`. Stopwords ES/EN inline. Score weighted: 0.30 corpus_size + 0.20 recency + 0.20 diversity + 0.30 quality. Gate `N<3 → cap 0.29` evita confiar en muestras chicas (un solo post approved daría falso "emerging" sin el gate).
- **Wire al endpoint**: `POST /api/v1/content/generate` (handler v3) ahora llama `use_brand_dna.build_dna_for_client(client_id)` → `build_rafa_system(client, ctx, dna, ...)`. **Por fin RAFA persona deja de ser dead code** — se inyecta como system block con cache_control ephemeral, enriquecido con tono / keywords / sample posts del cliente y guidance condicional según `dna.confidence_label()` (weak / emerging / strong).
- **Observabilidad**: metadata del draft persistido en `content_lab_generated` ahora incluye `brand_dna_score` + `brand_dna_label`.

8 archivos nuevos (1 domain + 4 application + 1 infra + 1 helper API + 1 test) + 1 modificado.

### Tarea 4 · ARIA lee `agent_memory` (commit 8a6a415)

ARIA ya **NO olvida** entre turnos. Antes de llamar a Claude:

- Nuevo `aria_memory_repository.fetch_recent_for_owner(client_id, reseller_id, limit=10)` filtra `agent_code IN ('aria','aria_1','aria_2','aria_3','aria_4')` (cubre legacy + futuro) y respeta el owner real (cliente o reseller).
- Nuevo `_aria_memory_context.load_and_format_memory(...)` orquesta repo → formato markdown legible:
  ```
  # MEMORIA RECIENTE (últimas interacciones con este cliente)
  - [hace 3h · ✓] Preguntó: "qué hago en IG" → Respondiste: "publicá martes 7pm"
  - [hace 1d · ✗] Preguntó: "subir precios" → Respondiste: "no, eso aleja clientes"
  ```
  Token-aware: max 500 tokens, trunca por filas y por palabras (12 user / 18 response).
- En `use_aria_message`: 3 líneas — import + `memory_block = load_and_format_memory(...)` + concat al system prompt (después de `build_system_prompt`).
- Best-effort total: si no hay owner / corpus vacío / Supabase down → `""` → ARIA funciona idéntica a hoy. Cero regresión.
- Bonus: `conftest.py` con env vars dummy para que los tests no rompan en `app.config.settings` import (sin afectar prod).

Cierra parcialmente el ciclo P5 (aprendizaje honesto): ARIA escribía memoria desde Fase 1 pero **nunca la consumía**. Ahora sí.

---

## 4. Estado de producción al cierre

| Componente | URL / Identificador | Estado |
|---|---|---|
| Frontend Vercel | `https://omega-two-wine.vercel.app` | UP · HTTP 200 · X-Vercel-Cache HIT · `Last-Modified` post-push consistente con deploy nuevo |
| Backend Railway | `https://omega-production-3c67.up.railway.app` | UP · `/health` 200 (`{"status":"healthy","version":"2.0.0","agents":"37/37"}`) · `/docs` 200 · 210 routes en openapi |
| Supabase Project | `rwlnihoqhxwpbehibgxu` (Omega MR) | UP · 15 migraciones aplicadas (00014 + 00015 nuevas hoy) |
| GitHub repo | `github.com/raisenomega/Omega` (privado) | main al día · head `8a6a415` · branch sincronizado con origin |

**Limitación de verificación**: ni Railway CLI ni Vercel CLI estaban autenticados en la sesión. Los health checks responden 200 y los headers Vercel cuadran con deploy fresco, pero certeza 100% del deploy nuevo (vs serving anterior) requiere `railway login` + `vercel login` + abrir dashboards.

---

## 5. DEBT nueva registrada (Sprint 2)

**DEBT-044 — Persistir Brand DNA computado + cron refresh** · ~8h · Medio (UX latencia + costo cache)

- **Hoy**: cada `POST /api/v1/content/generate` recomputa BrandDNA on-demand (1 SELECT a `brand_voice_corpus` + builder en memoria · ~50-100ms latency extra · ~20 rows).
- **Problema**: a escala 100+ requests/día/cliente es costo+latencia evitable. Además rompe cache_control ephemeral del system block de RAFA cuando el corpus cambia entre requests.
- **Fix Sprint 2**:
  1. Migración `00016_client_brand_dna.sql` con tabla `client_brand_dna(client_id PK FK clients, dna_jsonb jsonb, score float, last_computed_at timestamptz, last_corpus_size int)` + RLS
  2. Cron diario 3am en APScheduler que itera clients activos y UPSERT del DNA computado
  3. On-write trigger en `brand_voice_corpus` que setea `last_computed_at=null` para invalidar
  4. `use_brand_dna.build_dna_for_client()` lee tabla primero · fallback compute on-demand si stale o ausente
- **Beneficio**: cache hit rate Anthropic mucho mayor (DNA estable día completo) + latencia P95 reducida ~80ms

Registrada en `SOURCE_OF_TRUTH.md §6` al cierre de Tarea 3. Total deuda actualizada: **650h → 658h**.

---

## 6. Warnings pre-existentes (sin tocar en Sprint 1)

Los 3 warnings que reporta `scripts/validate-before-push.sh` y que **NO** son consecuencia de Sprint 1 (estaban antes · no se introdujeron · no se cerraron):

1. **G9 · Mock/fake/dummy en código de producción** (4 hits en handlers legacy)
   - `backend/app/agents/monitor_agent.py:87` — HTTP skip en Railway con mock data
   - `backend/app/agents/orchestrator_agent.py:142` — Execute "mock for now"
   - `backend/app/api/routes/agents/handlers/execute_agent.py:104,108` — Fallback mock + mock success message
   - Todos en handlers `/api/v1/agents/*` estilo Lovable · cubre DEBT-030 cleanup en Fase 3

2. **C4 · 53 archivos backend entre 75-100 líneas** (grace period DEBT-014 + DEBT-017)
   - El conteo **NO subió** por Sprint 1 (todos los archivos nuevos quedaron ≤75L · solo `use_aria_message.py` cruzó de 77 a 79, dentro de su mismo bucket warning ya contado)
   - Refactor por bounded context en Fase 3

3. **T5 · Pytest no disponible en el hook**
   - El hook intenta correr pytest pero no encuentra el ejecutable adecuado en el shell del hook (necesita activar venv)
   - Workaround manual usado en Sprint 1: `cd backend && ./venv/Scripts/python.exe -m pytest app/bc_cognition/`
   - Mejora pendiente: ajustar el hook para detectar venv automáticamente · no bloqueante hoy

---

## 7. Próxima sesión · prioridades Sprint 2

```
P0 · Generación de imagen con Nano Banana end-to-end
     - Wirear nano_banana_adapter (ya existe en bc_cognition/infrastructure) al endpoint /generate-image
     - Persona POIX (visual creator) nueva en bc_cognition/domain/personas/
     - Brand DNA visual: extender BrandDNA con visual_style derivado de brand_files
     - Endpoint POST /api/v1/content/generate-image retorna URL pública persistible (depende de P1)

P1 · Resolver DEBT-018 (URLs temporales → Supabase Storage)
     - Hoy: imágenes Nano Banana se devuelven como data URIs base64 (>1MB c/u)
     - Crear bucket `generated-images` en Supabase Storage + RLS (public read · service_role write)
     - Reemplazar return en bc_cognition/infrastructure/_image_compat.py por upload + URL pública
     - Crítico antes de producción real · data URIs no aptas para DB ni para compartir en redes
     - Migración 00017_generated_images_bucket.sql

P2 · A/B Variaciones 3 versiones (solo plan PRO)
     - Extender POST /content/generate con flag variations=3 (gated por client_plan)
     - RAFA genera 3 versiones con frameworks distintos en paralelo (Anthropic message batch)
     - Cliente elige una en UI · feedback alimenta agent_memory + brand_voice_corpus
     - Check de billing_v3 antes de habilitar (rechazar 403 si plan != PRO)
     - Spec en CONTENT_LAB §9.1

P3 · Virality Score V1
     - Función pura compute_virality_score(text, platform) -> float en bc_cognition/domain
     - Heurísticas iniciales: hook strength (0-3 primeras palabras), CTA presencia/calidad, emoji density, hashtag count, longitud relativa a benchmarks de plataforma
     - Adjuntar al output de cada generación como metadata.virality_score
     - Calibración con data real en Sprint 3 (necesita feedback loop activo de Meta API)
     - Spec en CONTENT_LAB §9.2

P4 · DEBT-044 · Persistir Brand DNA + cron refresh
     - Migración 00016 client_brand_dna table + RLS + indexes
     - Cron diario 3am en APScheduler · recompute por cliente activo · UPSERT
     - On-write trigger en brand_voice_corpus invalida last_computed_at
     - Refactor use_brand_dna · read tabla primero · fallback compute si stale (last_computed_at < now() - 24h o IS NULL)
```

Las tareas P0 + P1 están acopladas (P0 necesita el bucket de P1 para devolver URL real). Recomendación: arrancar Sprint 2 con P1 primero (storage bucket + migration) → luego P0 (wire del adapter + persona POIX).

---

## 8. Migraciones aplicadas en Sprint 1

```
00014_prompt_vault.sql               · HOY · tabla canónica + RLS + UNIQUE original
00015_prompt_vault_slot_name.sql     · HOY · ADD COLUMN slot_name + REPLACE UNIQUE (resolver 4 colisiones)
```

Ambas aplicadas vía `supabase db push --linked` y confirmadas por owner antes de seedear.

---

## 9. Estado del sistema al cierre

```
✅ 4 commits Sprint 1 en origin/main (head 8a6a415)
✅ 22 archivos nuevos · ~866 LOC insertions
✅ 18/18 tests pass (4 brand_dna_builder + 5 aria_memory_context + 9 routing_table existentes)
✅ validate 10/10 verde
✅ Cero breaking changes (legacy content_lab + personas existentes + use_aria_message contract · todos intactos)
✅ Cero violaciones C1/A2/I1/G6 nuevas
✅ Brand DNA Engine operativo · RAFA persona enchufada al pipeline real · ARIA con memoria
✅ DEBT-044 documentada en SOURCE_OF_TRUTH §6
✅ Total deuda: 658h (~16 semanas full-time)
✅ Railway + Vercel auto-deployed (health checks 200)
```

---

**Cierre 21 may 2026** · firmado: Claude Code (Sprint 1 ejecutivo) + Jorge Ibrain (CEO Raisen).

🐢💎 No velocity. Only precision.
