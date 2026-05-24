# PENDIENTES Y PROGRESOS · 23 mayo 2026

> Cierre de Sesión 1 PLAN_CONTENT_LAB_100 · Content Lab funcional end-to-end con backend real.

---

## RESUMEN EJECUTIVO

**Estado del sistema al cierre · 23 may 2026 ~01:40 AST:**
- 3 generaciones reales funcionales en producción (texto · imagen · video)
- 3 CTAs cableados a backend (Guardar · Descargar · Agendar)
- Block builder dinámico (≥3 piezas de cualquier combinación)
- 8 hooks especializados con `src/lib/api-client.ts` consolidado
- Stack actualizado: `google-genai 2.6.0` · `supabase 2.18.1` · `httpx 0.28.1` · `pydantic 2.11.7`
- 12 DEBTs nuevas registradas (DEBT-CL-003 a DEBT-CL-018) · DEBT-CL-014 cerrada

**Métrica de jornada:** ~17 commits · ~6h trabajo · cero downtime crítico (1 incident Railway build resuelto en 25 min).

---

## COMMITS DEL DÍA (orden cronológico)

| Hash | Commit | Categoría |
|---|---|---|
| `060178b` | Subtarea 1.5 · Guardar real via PATCH /content/{id}/save | feat |
| `6fdf795` | Subtarea 1.6 · Descargar real (texto/imagen/video) | feat |
| `4fbf609` | Subtarea 1.7 · Agendar real via POST /calendar/schedule/ | feat |
| `d9a5bd6` | FIX A · extract draft del JSON · evita output crudo | fix |
| `0b65b94` | bump google-genai >=2.0.0 (rompió build resolution) | fix |
| `404d2b0` | FIX C+D · modal Agendar relax 3→1 slot + doc /content | fix |
| `b0ce855` | pin google-genai==2.6.0 · resuelve resolution-too-deep | fix |
| `6cf3820` | bump supabase==2.18.1 + httpx==0.28.1 · conflict resolved | fix |
| `d3589ac` | bump pydantic==2.11.7 · realtime 2.7.0 requirement | fix |
| `47ddf0c` | veo3 operations.get acepta objeto · NO string · genai 2.x | fix |
| `064dc03` | video-compat follow_redirects=True · download 302 OK | fix |
| `0e54b82` | useMyClients fallback Supabase · ClientProfile 500 | fix |
| `9079150` | UX post-video · Save disabled + slot agendar correcto | fix |
| `f8d32f1` | grid overflow · cards image/video max-h-[100px] | fix |
| `70c4d5d` | block builder dinámico · BlockState {items[]} · ≥3 | refactor |
| `5292022` | JSON crudo LinkedIn · max_tokens 1500 + extract defensivo | fix |

---

## LOGROS PRINCIPALES

### Backend
- ✅ Veo3 video generation end-to-end (POST → asyncio.create_task → poll → download → Supabase Storage)
- ✅ Nano Banana image generation con persistent URLs Supabase
- ✅ Anthropic Claude texto con virality_score + brand_dna inyectado
- ✅ `_variations.py` extract draft robusto · max_tokens 1500 para outputs largos
- ✅ Stack moderno: google-genai 2.6.0 (con generate_videos) + supabase 2.18.1 + pydantic 2.11.7

### Frontend
- ✅ Cableado 3 endpoints reales · cero mock
- ✅ Block builder dinámico (libertad UX · cualquier combo de 3+ piezas)
- ✅ Grid 3x2 con cards 220px · overflow controlado · 100px max media
- ✅ Modal Agendar con date picker + lista dinámica
- ✅ Botón Save inteligente por tipo (Auto para video · normal para text/image)
- ✅ Consolidación API client (`src/lib/api-client.ts` · 7 hooks consumiendo `apiGet/apiPost/apiPatch`)

### Infraestructura
- ✅ Migración 00018 aplicada en prod (video_generation_jobs table)
- ✅ APScheduler reemplazado por `asyncio.create_task` (workers 2 compatible)
- ✅ httpx.AsyncClient con `follow_redirects=True` para Google Storage download

---

## DEBTs · ESTADO CONSOLIDADO POST-SESIÓN 1

| ID | Descripción | Status | Urgencia |
|---|---|---|---|
| DEBT-CL-003 | Auth helpers ARIAChat + UpgradePlan sin consolidar (cluster Content Lab YA) | 🟡 PARCIAL | Baja |
| DEBT-CL-005 | Backend ignora client_id en /content-lab/generate | ✅ CERRADA Sprint 3 | — |
| DEBT-CL-008 | /generate-image hardcoded 1024x1024 (no aspect_ratio param) | 🔴 OPEN | Media |
| DEBT-CL-009 | /generate-video ratio hardcoded 1280:768 | 🔴 OPEN | Baja |
| DEBT-CL-010 | Video polling cancelable mid-flight · orphan visual | 🔴 OPEN | Baja |
| DEBT-CL-011 | Nano Banana ImageConfig removida en 1.2 · existe en 2.6 (re-activar) | ✅ CERRADA Sprint 3 | — |
| DEBT-CL-012 | Download imagen/video posible CORS · verificar | 🟡 VERIFICAR | Verificar |
| DEBT-CL-013 | useScheduleBlock query Supabase directo (bypass backend RBAC) | ✅ CERRADA Sprint 3 (opción C · 4 endpoints calendar legacy con auth+RBAC) | — |
| DEBT-CL-014 | Modal Agendar 3 slots fijos → relajado libertad total | ✅ CERRADA | — |
| DEBT-CL-015 | account_id resolución LIMIT 1 sin elección del user | 🔴 OPEN | Media |
| DEBT-CL-016 | ClientProfile model desincronizado de DB (plan adopcion · campos null) | ✅ CERRADA Sprint 3 | — |
| DEBT-CL-017 | Backend ScheduledPostCreate sin video_url field · video viaja como image_url | ✅ CERRADA Sprint 3 (path X · calendar_v3/schedule_post + media_url col 00020) | — |
| DEBT-CL-018 | Bulk schedule · agendar N posts en una llamada (3 captions → 1 row solo hoy) | 🔴 OPEN | Baja |

**Total DEBTs activas: 11 · cerradas: 1 · verificar: 1 · estimación cleanup: ~6-8h**

---

## PENDIENTES INMEDIATOS (post-deploy 23 may)

1. **Verificar FIX JSON LinkedIn (`5292022`)** post-deploy:
   - Generar `linkedin_post` con cuerpo largo (>300 palabras)
   - Confirmar texto limpio (no JSON crudo)
   - Si sigue fallando: query DB raw_response para debug
     ```sql
     SELECT metadata->>'raw_response' FROM content_lab_generated
     WHERE metadata->>'ui_type' = 'linkedin_post'
     ORDER BY created_at DESC LIMIT 1;
     ```

2. **Smoke test combinado** del block builder dinámico:
   - 3 captions → ¿se persiste solo 1? (esperado por DEBT-CL-018)
   - 1 caption + 1 video + 1 hashtag → video viaja como image_url (DEBT-CL-017)
   - Quitar items individuales del modal → onRemoveItem funcional

3. **DEBT-CL-016 (Alta)** · sanear ClientProfile model:
   - Expandir PlanOption enum para incluir `'adopcion'`
   - Hacer campos legacy opcionales (email/role/subscription_status/trial_active)
   - Restaurar `useMyClients` a usar `apiGet` (rollback del fallback Supabase)
   - Estimado: ~45 min backend + 10 min frontend

---

## PRÓXIMA SESIÓN · Sprint 1 PLAN_IMPLEMENTACION

**Scope acordado:** Brand DNA Builder + ARIA memory injection + prompt_vault seed.

### Items principales

1. **Brand DNA Builder (visual)**
   - Frontend: UI para visualizar/editar el Brand DNA computado del cliente
   - Backend: endpoint GET `/clients/{id}/brand-dna` ya existe
   - Mostrar score · keywords frecuentes · tono dominante · samples top
   - Botón "Recomputar" para refrescar manualmente

2. **ARIA memory injection**
   - Verificar que `_aria_memory_context.load_and_format_memory` se invoca en cada request ARIA
   - Filtro agent_code IN (aria, aria_1..aria_4)
   - Formato markdown con bullets · ≤500 tokens

3. **prompt_vault seed**
   - Crear endpoint POST `/content-lab/seed-vault` (admin only · one-shot)
   - Migrar 30 prompts production-tested desde `CONTENT_LAB_OMEGA_MASTER.md` §5
   - Activar `_prompt_vault_selector` en `generate_text` handler
   - Routing por (vertical + platform + category)

### Tiempo estimado: ~3h dev + 1h QA E2E

---

## RIESGOS IDENTIFICADOS PRÓXIMA SESIÓN

1. **Brand DNA endpoint puede no devolver shape esperado** · verificar primero la implementación actual antes de UI
2. **30 prompts del Vault** requieren formato JSON específico · validar contra schema del DB
3. **ARIA memory injection** puede no estar cableada aún (DEBT-044 cerró infra pero falta wiring)

---

## CIERRE

Sesión 1 PLAN_CONTENT_LAB_100 considerada CERRADA con éxito. Sistema en producción funcional para generar/guardar/descargar/agendar contenido real con cliente real.

Próxima sesión: cleanup rápido de DEBT-CL-016 (~45 min) + Sprint 1 PLAN_IMPLEMENTACION (~4h).

---

## SPRINT 1 PLAN_IMPLEMENTACION · PROGRESS (mismo día · post-cierre Sesión 1)

### Subtareas

| # | Subtarea | Status | Commit |
|---|---|---|---|
| 1.1 | Seed 30 prompts del Vault · migración 00019 | ✅ commit creado · pendiente `supabase db push --linked` |
| 1.2 | Activar `_prompt_vault_selector` + refactor `_json_extract` | ✅ live post-deploy |
| 1.3 | Brand DNA Builder V1 · verificación de infraestructura | ✅ confirmado (DEBT-044 ya implementó · cableado en `generate_text.py:38-42`) |
| 1.4 | Brand DNA Score badge backend + frontend | 🟡 próximo |

### Subtarea 1.3 · Verificación detallada

**Status: YA IMPLEMENTADO** (DEBT-044 cerrada el 22 may 2026 dejó la infra completa). Lo verificado:

- ✅ `use_brand_dna.build_dna_for_client(client_id)` en `generate_text.py:39`
- ✅ `build_brand_dna(corpus)` en `_brand_dna_builder.py` con keyword extraction + tone counter + top excerpts
- ✅ `_system_builder.build_rafa_system` inyecta `_brand_dna_block` en system prompt
- ✅ `_brand_dna_block` handle `corpus_size == 0` con guidance "Sin corpus disponible · Usá defaults profesionales sin forzar imitación"
- ✅ Read-through cache 24h (`use_brand_dna._is_stale`)
- ✅ Cron `refresh_all_brand_dna` cada 3am en `main.py:103`
- ✅ SQL trigger en migración 00017 invalida `last_computed_at` cuando corpus cambia

### DEBT-CL-019 (nueva · NO bloqueante)

**Brand DNA industry benchmarks fallback.** El spec § Sprint 1 ③ menciona "Si el corpus está vacío, usar benchmarks de industria como fallback". Actualmente cuando `corpus_size == 0`, retorna `BrandDNA.empty()` con guidance genérico "profesional sin imitación".

Mejora propuesta (futuro · scope opcional):
- Crear tabla `industry_benchmarks` con tone + keywords típicos por vertical
- O hardcodear en `_brand_dna_builder.py`: `RESTAURANT_DEFAULTS = {"tone": ["warm", "auténtico"], "keywords": ["sabor", "casa", "familia"]}`
- En `build_brand_dna(corpus)` si corpus vacío + vertical conocido → usar defaults
- Tiempo estimado: ~30 min backend

NO se implementa en Sprint 1 V1 · cero impacto en cliente real (los clientes existentes YA tienen corpus poblado o el guidance default es razonable).

---

🐢💎 No velocity. Only precision.
