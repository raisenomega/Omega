# ESTADO OMEGA · Documento Vivo · Última actualización: 23 jun 2026 (**ARCO 2 CERRADO · decisión del owner EJECUTADA** · 4 commits `2b6f189`→`ab62914` · raisenomega · gate 15/15 c/u. **(1) Meta-analytics RETIRADO completo** (front+back · `2b6f189`/`c91fd4e`): borrados useMetaOAuth/useMetaChip/MetaIntelChip/meta_oauth/_meta_insights + tests · la sección Analítica y los chips de Inteligencia quedan **solo Google**. Razón: duplicaba seguidores/alcance/engagement IG/FB que **Zernio YA entrega** + evita que el Arco 3 (Meta-Ads · Marketing API) se cablee por error con este connect de insights orgánico Graph v21 deprecado. **(2) GA4 Vía A CERRADO** (`ab62914`): el connect Google ahora persiste el property_id elegido (picker `accountSummaries.list` · scope analytics.readonly ALCANZA · contrato verificado vs doc OFICIAL) → GA4 sessions + GSC funcionan al conectar. **DEBTs cerradas-por-retiro:** DEBT-ANALYTICS-OAUTH-PER-CLIENT-META (ya cerrada en código `955a558` · el ESTADO la daba "abierta" = stale · ahora OBSOLETA), DEBT-META-OAUTH-V21-LATENT (mina v21 desactivada: meta_oauth borrado), DEBT-META-CHIP-METRICS-2026 (_meta_insights borrado). **DEBT-META-PUBLISHER-DEAD NO aplica** (es de `publishing/` · fuera de este arco · sigue muerta sin importador real, solo un comentario en zernio_adapter). Nota honesta: probado a nivel código/conexión · el "número real >0" requiere sitio con tráfico + tag GA4 (Omega Raisen sin web aún · pendiente del owner, **NO deuda de código** · gap GA4 cerrado acá, no diferido). NOVA/ARIA/limits intactos.) · 23 jun 2026 (**ARCO 2 CÓDIGO COMPLETO en prod — PERO UTILIDAD EN DUDA** · A+B1+B2+B3a+B3b (`d695abc` · Google+Meta connect para INSIGHTS/leer-métricas: A Google per-negocio · B1 Meta per-negocio · B2 hooks clientId de ruta · B3a popup `/oauth/return`+BroadcastChannel · B3b UI sección "Analítica" tab Cuentas, cero-Zernio · gate 15/15 c/u). **El owner siempre quiso ADS (gestión de campañas = Arco 3/LUAN), NO analytics** → el connect del Arco 2 podría ser **duplicado/muerto** frente al Arco 3. **PRÓXIMA SESIÓN = UNA SOLA TAREA, read-only, sin tocar código: decidir qué hacer con el Arco 2** (mantener/retirar/refactor · análisis a fondo contra el código real · con evidencia · entregar y esperar review ANTES de cualquier otro paso). **REGLA INVIOLABLE: cero confiarse de una sola línea · lo no confirmable = "NO CONFIRMADO"** (por el error §3.1). NO investigar plataformas/recon/docs aún · solo la decisión del Arco 2. Falta e2e del Arco 2 = pasos del owner (Fase C config OAUTH_REDIRECT_BASE+callbacks google/meta · Fase D conectar cuenta real). NOVA/ARIA/limits intactos.) · 23 jun 2026 (**ARCO 2 · FASE A CERRADA en prod** · `b5e8a10` · raisenomega · gate 15/15. `/oauth/google/authorize`+`/status` toman el `client_id` del Switcher (query requerido) + ownership vía `resolve_client_or_403` (= `get_client`+`user_owns_client` · **MISMO ownership que `chips.py`** que consume el mismo token Google) en vez de `find_client_for_user`. `callback` intacto (client_id del state firmado). 5 tests (corazón = ajeno→403 en authorize **Y** status, vía deps del resolver = aislamiento real probado · + authorize_propio firma ESE client_id en el state) · line-neutral (net 0 · ratchet 177≤178). **DEBT-ANALYTICS-OAUTH-PER-CLIENT CERRADO (Google).** 🆕 **DEBT-ANALYTICS-OAUTH-PER-CLIENT-META** abierto (`meta_oauth.py` mismo bug user-based líneas 76/98/176 · mismo diff · después). **Fase B (próximo):** UI + el hook `useGoogleOAuth.ts` DEBE pasar `activeBusinessId` o da 422. NOVA/ARIA/limits intactos.) · 23 jun 2026 (**NOCHE DE DEBTs · 4 cerrados + sonda Arco 2** · raisenomega · gate 15/15. **DEBT-047 jobstore persistente RESUELTO** (cadena de 3: el `@` del password rompía el parse de create_engine → fix `build_jobstore_url`/URL.create `5bec3ff` · luego la directa `db.<ref>.supabase.co` es **IPv6-only** y Railway es IPv4 "Network unreachable" → fix env-var `JOBSTORE_DATABASE_URL` `5d96cd9` apuntado al **session-pooler IPv4** · **apscheduler_jobs vive · 27 jobs persistentes** · sobrevive restarts de verdad · next_run snapshot 10:00 UTC). **#2 omega_worker_logs** (migr 00073 `793a9dc` · base_worker escribía a tabla inexistente → PGRST205 · creada per-client + RLS verbatim · NO confundir con omega_error_registry · cerrado). **Hallazgo timezone:** el scheduler corre en **AST** → el cron snapshot dispara 6am AST = **10:00 UTC** (no 6am UTC) · label corregido `23996e0`. **captured_at** = primera-captura documentado (Opción 3 · freshness=metric_date, no captured_at). **#3 dockerfile-secrets:** diagnosticado · **NO es código** (no hay Dockerfile del backend · nixpacks.toml limpio) · acción Railway pendiente (Ibrain: secrets runtime-only). **#4 cron-missed-1s:** cierra con #1 (era síntoma del MemoryJobStore). **Sonda Arco 2 (read-only):** GOOGLE_CLIENT_ID/SECRET presentes en Railway · `_google_insights.py` completo (GA4 sessions + GSC clicks/impresiones real · sin stubs) · OAuth backend **per-client** (state firma client_id · oauth_tokens UNIQUE client_id+provider · VACÍA) · GAPS: el authorize toma el client del **user** (find_client_for_user) no del Switcher (= DEBT-ANALYTICS-OAUTH-PER-CLIENT) · falta UI "Conectar Google" (`useGoogleOAuth` existe, ningún componente lo usa) · `OAUTH_REDIRECT_BASE` malformado (full-path → redirect_uri doble · verificar Railway+Google Cloud). Punto de continuación detallado abajo (## ARCO 2). NOVA/ARIA/limits intactos.) · 22 jun 2026 (**SESIÓN ARCO ANALYTICS COMPLETO + ARCO 1 PIPELINE** · identidad raisenomega · gate 15/15 c/u. **(A) ARCO ANALYTICS cerrado end-to-end en prod** (`08a87b8`→`39a21da`): (1) Tab Cuentas honesto + Reddit (`08a87b8`→`189d6a0` · migr 00071 CHECK 6→7 · fuente única 7 conectables + 4 coming-soon · seguidores sintético→real Zernio/"—" · test sincronía CHECK↔constante). (2) /health honesto (`d7f3d57` · 3 false-greens muertos: status hardcodeado→derivado · count-else-37→None · "37/37"→agents_active int · verif prod). (3) Panel ampliado (`d11d439`→`829274d`+guard `3ec085f` · 5 métricas acumulado · selector período eliminado [false-control: daily-metrics all-history] · ER "histórico" · GrowthChart guard <2 puntos · verif MB reach155/ER5.8 + OR reach11/ER18.2). (4) Chip de redes (`5475c04`+`39a21da` · filtra por red · 3 trampas P1: growth no-IG→"no disponible" · best-time→"del perfil" · tabla solo "Todas" · FB reach0→ER"—" verif). → **DEBT-034 resuelta · bug "28 seguidores" cerrado.** **(B) ARCO 1 PIPELINE histórico** (`63a617c`+`b6efc01` · prod): tabla `social_metrics` (migr 00072 · RLS verbatim verificada 00072≡00001≡prod-vivo · CHECK 7 · NULLABLE) + cron diario 6am `social_metrics_snapshot` (26→27) + builder puro + 10 tests. **Fase 3 viva 6/6:** 80 filas reales (MB/OR/Wudi/Zafacones) · aislado · valores==Zernio (155/11 exacto) · NULLs honestos (FB reach0=0-real) · idempotente (RUN2=80 cero dup). Per-día actividad real + snapshot followers · llave client_id+profile_id-traza · tablas hermanas ads/web futuras (no jsonb). **Solo-ESCRITURA** (panel live-read · LUAN futuro). Pendiente: cron-status=27 en vivo (owner logueado) · mañana confirmar cron auto 6am. **NOVA/ARIA/limits intactos.**) · 20 jun 2026 (**SESIÓN REX POR-RED + DASHBOARD UNIVERSAL + ARIA RETRACCIÓN** · 4 commits en prod `1727500`→`a61bec9` · gate 15/15 c/u · identidad raisenomega. **(1) REX límite POR RED** (`1727500`): holdeaba 1 de 3 posts agendados a la misma hora en 3 redes distintas por contar publicaciones COMBINADAS por cliente (cap 3) → ahora cuenta por `(client_id, platform)`, cada red su cupo. **Rename del archivo sagrado** `MAX_POSTS_AUTO_PER_DIA_CLIENTE`→`MAX_POSTS_AUTO_PER_DIA_RED` (3→24) con **ritual SHA1 completo** (test rojo→cambio→rotar baseline `ee472c1d`→`213e3c01`→gate 15/15 · personas X2 intactas) · `count_published_today`→`count_published_today_by_platform` (dict · Counter) · campo `posts_today`→`posts_today_platform` · UC incrementa por-red. Anti-spam real = espaciado 2h; 24/red = backstop bajo el techo IG (100/24h); el `3` del bulk-spacer es eje DISTINTO (reparto al agendar · desacoplado). Test del bug: 3 redes misma hora → 3 publican. **(2) Dashboard 3 elementos UNIVERSALES** (`9dc8818`): barra de plan + "Seguridad de tu cuenta" + "Sugerencias de ARIA" estaban gateados por `!isOwner` (invisibles para resellers) → ahora se scopean al **negocio activo del Switcher** (`activeBusinessId ?? clientId`), visibles para cualquier usuario. Barra = plan del negocio activo · Seguridad = sesión per-usuario (session-report por user.id) · ARIA = del negocio activo. **Aislamiento triple capa** (switcher valida cartera real + useMyClients backend-scoped + RLS/ownership). Cierra deuda "barra gated !isOwner". Frontend-only 1 archivo. **(3) ARIA retracción de sugerencias STALE** (`a61bec9`): una unread persistía tras dejar de aplicar su condición (Mail Boxes Enterprise mostraba "upgrade a PRO" generada cuando era basic) → reglas a **tri-estado** (True=aplica/emite · False=negativo DETERMINADO/retracta · None=indeterminado/conserva · query falla→None→no agresivo) + `writer.retract_unread(client_id,type)` (scope por client_id · sin migración · reusa is_read) · 3 tests (bug + indeterminado + positivo). **(4) Docs** (`cc9e189`): DECISIÓN-PRECIOS-2026 (Adopción $0/Básico $29/Pro $97/Enterprise $269 · NO implementar · sesión dedicada) + DEBT-VITEST-FLAKE-PREPUSH + DEBT-ARIA-SUGGESTIONS-TEXT registradas. **Verdades vivas verificadas:** REX **respeta la hora agendada** (sin espaciado propio en su camino · gate sin check de horas · `fetch_due_posts` toma todo lo due · el espaciado vive solo en el bulk-spacer) · ARIA sugerencias **aisladas por negocio** (motor de 4 reglas sobre señales reales · NO array estático · lo genérico es solo el wording = DEBT-TEXT). NOVA/ARIA/limits SHA1 intactos salvo el rename intencional de limits con ritual.) · 16 jun 2026 (**SAGA SEGURIDAD POST-FASE-2 CERRADA · CI verde + 0 deuda JS** · 9 commits `5f9edb4`→`4662b6b` · **confirmado en los RUNS REALES de GitHub** (Contract Gate + SENTINEL Dependency Scan + Build Stats todos VERDES · panel "Dependencias y CVEs: passed · JS 0/0/0"): el GitHub Action de P5 + SENTINEL atraparon deuda invisible al gate local y se cerró toda. **(1) Contrato 13→15** (`021b034` · autorizado owner): `DDD_REGLAS_OMEGA` sellado a 15 checks (el gate ya corría 15; alinea el contrato · sin SHA1 a rotar). **(2) CI frontend ROOT-FIX** (`e4c75cc`): el job frontend del Action estaba ROJO (`supabaseUrl is required` · `client.ts` llama `createClient` en module-load antes de que vitest exponga env). 1er intento (env-dummy en workflow `1eebc25`) **NO tomó en el run real** — LECCIÓN: el criterio de verde es el RUN de GitHub, no la repro local. Fix real = `vi.mock("@/integrations/supabase/client")` en `guardian-actions.test.ts` (mata la dependencia · test usa solo función pura) · verificado contra la condición REAL (env VACÍO → suite 13/13 · 54 passed). **(3) Node 20 deprecated** (`4cbc999`): bump `checkout@v5 · setup-node@v5 · setup-python@v6` en los 3 workflows. **(4) CVEs JS/npm COMPLETOS** (`8be2776` reporte → `9b47b45` 3 seguras → `4662b6b` vite@8): `npm audit` arrancó **9 vulns (1 crit · 5 high · 3 mod) · NUNCA se había auditado el lado npm** (toda la saga previa fue Python/pip-audit). Cerradas por fases: (a) seguras `npm audit fix` sin --force (vitest 3.2.6 CRÍTICA + form-data + ws) · (b) salto mayor coordinado **vite 5→8.0.16 + @vitejs/plugin-react-swc 3→4.3.1 + vitest 3→4.1.9** (lovable-tagger 1.3.0 ya soporta vite 8 · el audit sugería mal bajar a 1.0.20) + **override `esbuild:^0.28.0`** (el esbuild 0.25.12 que arrastraba lovable-tagger → 0.28.1 limpio). **VERIFICADO: npm audit = 0/0/0 · build ✓ · tsc 0 · vitest 4 → 54/54 · dev server `VITE v8.0.16 ready` · gate 15/15 · vite.config sin cambios.** **DEBT-JS-CVE CERRADA · cero deuda JS.** NOVA/ARIA/limits intactos.) · 16 jun 2026 (**FASE 2 AUDITORÍA EXTERNA COMPLETA · P5→P10** · 8 commits `da1dd9d`→`2bc8042` · gate **15/15** (era 13) · pytest 441 · vitest · tsc · build OK): cierre del arco deprecations + hardening + centralización + misc. **P5-P7** (ya cerrados): GitHub Action contract-gate `da1dd9d` · CORS fail-secure `0b0cc3d` · cron-status endpoint + fuente única crons `55ee329` · `_cors_policy` `250fe1c`. **P8a** (`dc2b097`): 30 `datetime.utcnow()`→`now(timezone.utc)` en 19 archivos (aware-safe · `_brand_dna_scoring` normaliza a aware-UTC AMBOS lados de la comparación recency → evita TypeError naive/aware que el default aware del builder destapaba · regresión `test_aware_now`) + `Query(regex=)`→`pattern=` + `@app.on_event`→`lifespan` (los 24 crons in-process dentro del lifespan · alineado `--workers 1` · fuente única `cron_registry`). **P8b** (`5de5500`): bump fastapi 0.109.0→**0.137.1** · starlette 0.35.1→**1.3.1** (saltó a 1.x) · uvicorn 0.27.0→**0.49.0** → **DEBT-FASTAPI-BUMP CERRADA** · pip-audit confirma 0 CVEs en los 3 → 8 IDs fuera del allowlist (43→35 deferidos) · verif openapi 260 paths + TestClient /health+status+calendar(401) + **lifespan startup vivo** (jobstore cae a in-memory DEBT-047 si DB no responde). **P9** (`268d2b2`): ~120 literales claude-{haiku,sonnet,opus} → `routing_table.MODEL_HAIKU/SONNET/OPUS` (única fuente · MODEL_IDS deriva) · **I2 INTACTO** (cada agente conserva su modelo) · `ai_provider_bedrock/vertex` ARNs DÉJADOS — el `-20250514-v1` es formato Bedrock **LEGÍTIMO**, hallazgo FALSO de la auditoría (verificado) · check nuevo gate "claude-* fuera de routing_table → warning". **P10** (`2bc8042`): LICENSE proprietary · **ratchet C4** (`scripts/c4-baseline.txt`=178 · >100L en dirs de gracia puede bajar, no crecer) · **code-splitting** React.lazy+Suspense en ClientDetail/Media/SecurityDevPage (bundle principal **1576→1448 KB** · 3 chunks nuevos SENTINEL 80/ClientDetail 48/Media 8 KB) · **mypy --strict** check WARNING 14/15 (1096 err · skip si ausente · pin `backend/requirements-dev.txt`) → **DEBT-MYPY-BASELINE** · **DEBT-TEMP-ENDPOINTS** registrada (run-now ya tras superadmin). **Calibración X5** (P10.1 · read-only prod): solo **3 filas / 2 clientes** (`7d9d4335` [0.78,0.88] · `7663aa55` [0.88]) todas ≥0.78 text · n<<3×20 → **DEBT-X5-CALIBRATION-MULTICLIENT SIGUE ABIERTA** (sin recalibrar). **DEBTs nuevas:** MYPY-BASELINE · TEMP-ENDPOINTS. **Gate ahora 15 checks** (ratchet C4 + claude-strings P9 + mypy P10.5). **NOVA/ARIA/limits_omega INTACTOS** (SHA1 sin rotar · X6 respetado). **Pendiente verif post-deploy: `/system/cron-status` 24/24 healthy en 1 worker + Vercel.**) · 16 jun 2026 (**SAGA X5 — VERIFICADA EN PROD · e2e visual owner 4/4 ✅** · 19 commits `f60ba50`→`0e530d5` · gate 13/13 · pytest 435 · vitest verde): cierre del arco completo Fase 1 + bugs + calibración + gaps. **(1) Fase 1 P0s** (workers 1 + check 12 · gate X5 con dientes · check 9 exit-code · purge jose + bumps + check 13 pip-audit). **(2) Ronda bugs post-deploy:** BUG1 estado loading "Agendar bloque" (`b596ff0` · hipótesis owner descartada con datos: era 409 pre-gate, no 422) · BUG2 bypass cuentas test en `variations_require_pro_plan` por email (`91813e6`) · BUG3 `extract_draft` repara JSON con newlines literales (`5bb02bc`) · over-blocking sin-corpus → PASS con rastro (`6f85755`). **(3) Damage gate X5 de 2 bandas** (`e7dce7c`): el 503 real era TRUNCAMIENTO de Haiku (max_tokens · `fac5c9b`), NO Supabase (mi diagnóstico inicial falso · owner corrigió) · escala anclada (`5c077c0`) · `SCORE_BLOCK_THRESHOLD=0.5` (<daño>422 `brand_voice_damages_brand`) / `SCORE_BRAND_BAR=0.7` (0.5-0.7 pasa con flag `below_brand_bar`) · calibración real afb9f578 (legítimo ≥0.62, dañino ≤0.15). **(4) Guardar-imagen** (`ef607ec`): el path async usaba job_id; el status ahora expone `content_id` real → check 1 ✅. **(5) Timezone −4h** (`4eddcab`): `toUtcIso` UTC explícito + backend rechaza naive (422) → check 2: owner puso 01:05PM, calendario 13:05 ✅. **(6) GAP SUPERVISADO CERRADO** (`86ccf93`): el approve del Modo Supervisado insertaba scheduled_posts SIN gate → ahora `save_content` rutea por el MISMO `check_or_raise` · **check 4 (el decisivo · código que no existía antes): "OYEEE LOCO…PENDEJO" aprobado desde supervisado → `brand_voice_damages_brand:=0.15` BLOQUEADO** · puerta trasera cerrada. **Ambos caminos de agendado (Content Lab block + Supervisado) ahora con damage gate.** Allowlist pip-audit +11 CVEs nuevos pypdf/starlette (`0e530d5` · el check 13 forzó el triage). Pre-push hook local sincronizado a 13 checks. **DEBTs nuevas:** SCHEDULER-SPLIT · X5-SCORE-AT-GENERATION · PYPDF/PILLOW/LXML/FASTAPI-BUMP · X5-CALIBRATION-MULTICLIENT · TZ-CLIENT-INTENT. SECURITY-KEYS-ROTATION sigue ABIERTA. Migración 00067 aplicada a prod. Cleanup: 4 drafts de prueba borrados (1121eb0a + agresivos Zafacones/Mail Boxes). **NOVA/ARIA/limits_omega INTACTOS.** **Próximo: Fase 2** (`PLAN_PARCHES_AUDITORIA_20260610.md`: husky+GitHub Action · /system/cron-status · CORS fail-secure · utcnow→aware+lifespan+bump fastapi [cierra starlette CVEs] · strings de modelo centralizados).) · 10 jun 2026 (**AUDITORÍA EXTERNA · FASE 1 P0s** · 6 commits `f60ba50`→`95ecf28` · **gate 13/13 · pytest 409 · vitest 52**: **P0-1** `--workers 1`+check 12+test anti crons-duplicados [scheduler in-process · 24 crons · DEBT-SCHEDULER-SPLIT] · **P0-2** gate X5 brand-voice draft→scheduled **CON DIENTES** [test G3 `98565c5` + scorer bc_cognition Haiku `routing_table:brand_voice_checker` + migración **00067** col `brand_voice_scored_at`+RPC `mark_brand_voice_scored` + cache `scored_at≥updated_at` + 422 `brand_voice_below_threshold:cid=score` + 503 con válvula `force_brand_voice` + override auditado en `agent_memory` + frontend toast `ac31c60`] · **P0-3** gate vitest/pytest por **exit-code** (ya no ciego · reportaba verde con suite roja) + guardian-actions jsdom [`d461a3e`] · **P0-4** purge `python-jose` (muerta+CVE) + bump multipart/requests/email-validator/dotenv/**PyJWT 2.10→2.13 (8 CVEs auth · verificado)** + check 13 pip-audit allowlist en archivo [`95ecf28` · ~13 CVEs cerrados · 32 deferidos → DEBT-PYPDF/PILLOW/LXML/FASTAPI-BUMP]. **Corrección de premisa de la auditoría:** asumió `brand_voice_checker` como SERVICIO existente; solo existía el SLOT en `routing_table` — NO había checker `(client_id,content_id)→score`, y la columna `content_lab_generated.brand_voice_score` existía desde 00001 pero **nunca se escribía**. **DEBT-SECURITY-KEYS-ROTATION sigue ABIERTA** (diferida a fin de proyecto · owner 10 jun). Migración 00067 aditiva → aplicar a prod ANTES del deploy. NOVA/ARIA/limits_omega intactos.) · 8 jun 2026 (sesión Opus 4.8 · features + seguridad · **vivo en prod:** Modal Supervisado completo (foto desde Biblioteca + editar caption + editar fecha · branch `add-photo-media-picker-modal` mergeada) + Aislamiento `/content-lab` por negocio (localStorage scopeado por businessId + cleanup legacy · `fix/content-lab-business-isolation` `7b75a1a` · verificado 4 negocios) + **track INCIDENTE-SEC-002: 16 endpoints IDOR remediados en 3 fases** (A scheduling orphan / B clients-legacy partial / C brand_files · delete de código muerto + 1 patch ownership · analytics=falso positivo · 0 features rotas · pointer SOURCE §6 · detalle `*.local.md`). **Deudas registradas:** SEC-001 (credencial · no rotada · triggers) · OBS-001 (trazabilidad ARIA) · OBS-002 (queryKey sin business · estimado real 9-12h) · DEBT-FUNC-001 (local). Convención: vulnerabilidades detalladas en `*.local.md` gitignored, pointers sanitizados en SOT) · 3 jun 2026 (**SPRINT 1 SENTINEL HARDENING** · HEAD `19b7717` · 7 capas en sesión: 4 CVE/dep-scan (`54727fb`) + 5 secrets-rotation (`e37fdec`) + 6 RLS-audit (`174f07d`) + 7-A AI-provider-router failover-prepared/Anthropic-only (`ffe4fdd`) + 9 observabilidad-runtime (`bd87b18`) + 10 performance-APM (`ac9429e`, cierra el error_rate de la 9) + 12 agentes-IA-health (`19b7717`) · migraciones 00050→00056 a prod · crons 16→21 · panel `/security-dev`→SENTINEL con 7 bloques nuevos data-real · regla P1 cada capa: verificar fuente antes de asumir (agent_log/omega_audit_log vacíos→fuentes reales · Railway/tokens ausentes→null honesto · cobertura legacy DEBT-023/024/025 siempre explícita) · pendiente próxima sesión: Capa 11 Integraciones · 3 Red/HTTP · 7-B Bedrock/Vertex (req creds AWS+GCP) · 8 Pentest · bridge GUARDIAN · spec viva local `SENTINEL_GUARDIAN_ENTERPRISE_COMPLETE.md` v2.1 gitignored · pendiente owner: disparar workflow GitHub `SENTINEL Build Stats` 1 vez) · 3 jun 2026 madrugada (HEAD `1816783` · panel SENTINEL final · chips clickeables + Ignorar/Fix funcional (migración 00049 `sentinel_issue_actions` aplicada) · Fix→Dev Chat existente (placeholder Sprint 8 · prompt copiable) · cero DEBT diferido) · 3 jun 2026 noche (HEAD `15f866a` · briefing fantasma fixeado (`aa23a1d`) + panel SENTINEL completo (botón scan + detalle per-componente HERMES style) · cero DEBT diferido) · 3 jun 2026 PM (HEAD `7627424` · SENTINEL des-cegado · migración 00048 + 3 filas reales E2E · DEBT-SENTINEL-BLIND CERRADA) · 3 jun 2026 (HEAD `36afac6` · CIERRE IDORs · #3 plan general · analytics `8b2da5e` + nova backend `715aab3` + página NOVA frontend `8262925` + iteraciones UX `6a0ce24`+`36afac6` · DEBT-IDOR-ANALYTICS + DEBT-IDOR-NOVA CERRADAS · auditoría 2-jun pusheada · 3 DEBTs nuevas registradas) · 1 jun 2026 PM (HEAD `a7a4d2d` · **HERMES v1.5 CERRADA** + **publicación Zernio construida F0→F3.6 y VERIFICADA EN VIVO** FB/IG/TikTok · DEBT-040 supersedida · DEBT-LIMIT1 `/publish/auto` cerrado · DEBT-IMAGE-ASYNC confirmada en vivo "se cae" · pendiente Zernio F4 rename + F5 wizard multi-negocio) · 1 jun 2026 AM (HEAD `cb585b6` · Switcher V1 CERRADO 100% + reconciliación censo · 4 deudas técnicas migradas a SOT §6 · regla de cierre de sesión añadida §7) · 29 may 2026 (Sprint 7 · DEBT-097 CERRADA · Modo Supervisado acotado: máquina estados P2/P3 + panel cola por-negocio + toggle · cron auto → DEBT-096 · DEBT-102 CERRADA widget "Qué aprendió ARIA" · cross-client → DEBT-033 · sync MCP v2.0 Zernio · DEBT-MCP-ZERNIO/ANALYTICS + 3 HERMES registradas · orden Sprint 8 re-locked) · 28 may 2026 (sesión 6 · DEBT-099+v2 CERRADAS · plan bar 7 estados · modelo reseller LOCKED · E2E prod ✅)

> **Fuente de verdad OPERACIONAL** (qué está hecho, qué falta, en qué orden).
> Fuente de verdad TÉCNICA (contratos DDD, arquitectura, detalle de DEBTs): `SOURCE_OF_TRUTH.md`.
> Este doc reemplaza los 8 `PENDIENTES_Y_PROGRESOS_*.md` (consolidados · detalle granular en git history).

---

## 🗺️ PANORAMA POR CAPAS vs VISIÓN (20 jun · % contra el alcance CANÓNICO)

- **Capa 1 — Plataforma operativa vendible: ~75-85%.** SaaS white-label, agentes core, publicación Zernio en vivo, REX autónomo, billing, seguridad auditada. Falta pulido pre-lanzamiento.
- **Capa 2 — Agentes CANÓNICOS (8 + SOPHIA · per `OMEGA_ROLES_CANONICO`): ~70-80%.** NOVA/ARIA/REX/Guardian/Sentinel + sub-cerebros `bc_cognition` vivos. **Los 57 agentes del catálogo comercial NO son alcance actual** — son fase futura post-capa 3/4 (verticales por industria/nicho). Medir contra 57 contradice el canon (57 = visión comercial, no operativos).
- **Capa 3 — Moat de contexto (3 capas de persistencia · backup estratégico + archivo R2): ~15-20%.** `agent_memory` pgvector parcial · el resto por delante · "el activo irreemplazable".
- **Capa 4 — Modelo comercial (marketplace, bundles, agentes vendibles): ~20%.**
- **CONJUNTO contra el alcance ACTUAL (excluye verticales): ~55-65% de la visión operativa.**
- **SECUENCIA del owner (20 jun):** capa 3 (moat) → capa 4 (comercial) → agentes verticales por industria/nicho. Primero **profundidad** (contexto irreemplazable), luego **monetización**, luego **ancho** (nicho). Construir 57 agentes antes del moat = ancho sin profundidad.

---

## 💲 DECISIÓN-PRECIOS-2026 (20 jun · DOCUMENTADA · NO implementar · sesión dedicada pre-launch)

Reestructuración de negocio (toca Stripe + planes DB + copy global + banners upgrade). **NO al vuelo · sesión dedicada, por partes.**

- **Estructura nueva:** Adopción **$0** (generosa en EXPERIENCIA no volumen · deja probar REX 1 vez · muestra features bloqueadas con "esto es Pro") → Básico **$29** (capado: sin Analytics/Crisis/Centro Intel · induce add-ons) → Pro **$97** (sube de $65 · todo desbloqueado · plan OBJETIVO) → Enterprise **$269** (sube de $199 · todo ×3 + ARIA 4 + soporte · plan META).
- **Posicionamiento:** "el agente autónomo REAL a precio de PYME" · Pro $97 < Hootsuite $99 (que ni publica solo) · Enterprise $269 > Apaya/Sprout $249 (autoridad premium).
- **Palancas:** cupo de GENERACIÓN (32/64/192) limita y empuja upgrade · add-ons rescatan margen de Básico · mensajes enfocados en AUTONOMÍA según plan.
- **Economía verificada (20 jun):** AI cost real bajo (Básico $1.58 · Pro $3.72 · Ent $10.43/mes) · Zernio $6/cuenta pocos clientes → $1 a escala · márgenes 84-92% a escala.
- **Implementar en sesión dedicada:** Stripe + planes DB + copy global + banners upgrade. NO al vuelo.

---

## 🟢 DEBT-ARIA-SUGGESTIONS-TEXT (20 jun · CALIDAD del contenido · NO urgente)

El **texto** de las Sugerencias de ARIA es estático: 4 plantillas fijas en `_MSG` de
`backend/app/api/routes/aria_v1/handlers/suggestions_create.py` (ej. "Con el plan PRO desbloqueás
posts ilimitados y más cuentas"). La **selección** de cuáles aparecen SÍ es real y per-negocio (motor
de 4 reglas sobre señales reales: actividad de publicación, plan, perfil, aria_level), y el aislamiento
por negocio está OK. Lo genérico es el **wording** → "parece" placeholder aunque la lógica sea real.
Fix futuro: generar el texto con datos reales del negocio (nombre/números/gaps · LLM o templates con
variables). Deuda de CALIDAD, no de aislamiento. Hermana del bug de retracción STALE (ese es liviano y
se cierra ya · ver reporte 20 jun: una sugerencia unread persiste tras dejar de aplicar su condición).

---

## 🟢 DEBT-VITEST-FLAKE-PREPUSH (20 jun · CONFIABILIDAD del gate · NO urgente)

El gate pre-push (CHECK 9 · Vitest) puede fallar **transitorio** por timing del setup de jsdom (~49s) — **no por código**. Frenó el 1er push de `1727500` (20 jun); el reintento pasó **15/15** con vitest directo **67/67** y el gate manual **15/15**. Es ruido que puede bloquear pushes legítimos. **NO urgente.** Si recurre: estabilizar el setup de jsdom (timeout / aislamiento del test runner). Deuda de **confiabilidad del gate**, no del producto. Hermana de [[gate-pytest-false-green]] / DEBT-VERCEL-NO-TSC-CHECK.

## ✅ DEBT-HERMES-CRON-TEST-TIME (21 jun · RESUELTA · hermana pytest de DEBT-VITEST-FLAKE-PREPUSH)

El test `test_cron_dispatch_ok_cuenta_la_alerta` (`workers/tests/test_hermes_alert_worker.py`) era un **flake temporal PRE-EXISTENTE** (verificado: fallaba en HEAD limpio, sin relación con analytics). Causa raíz: `run_hermes_alert_check` usaba `datetime.now(timezone.utc)` (hora de pared real) con ventana `_WINDOW_MIN=6`, pero el test anclaba `created_at` a un `_NOW` FIJO (`2026-06-21 12:00 UTC`) → corriendo después de las 12:06 UTC de ese día la fila quedaba "vieja" (fuera de ventana) → `alerted=0` → fallo. **Gate rojo a CUALQUIER hora salvo ~mediodía UTC del 21-jun → bloqueaba CADA push.** **Fix (refactor PURO · cero cambio de prod):** helper `_now()` como punto de inyección (prod sigue usando `datetime.now(timezone.utc)` real) que los 2 cron-tests mockean a `_NOW` → deterministas (el best-effort además se vuelve significativo: la fila queda en ventana → dispatch SÍ se llama → levanta → el cron sobrevive). Era deuda REAL, no inventada. Hermana de [[gate-pytest-false-green]].

---

## 🟡 DEBT-SENTINEL-BRIEF-NO-HEARTBEAT (21 jun · canal oficial · NO es bug de canal)

El brief diario de SENTINEL **dejó de llegar por email ~31 may** (3 semanas · confirmado Gmail del owner + Resend "last used 21 days ago"). **Causa raíz: NO es canal roto — es brief CONDICIONAL.** `sentinel_service.py` solo dispara `dispatch_sentinel_brief` `if total_issues > 0 OR score < 85` ("solo si hay algo que reportar"). Desde el hardening de junio **SENTINEL está sano** (score ≥95 sostenido · 0 issues) → la condición da False → el brief no se manda, por diseño. **El canal funciona:** `RESEND_API_KEY` válida (last-used 31 may), `alert_email_to` = `raisenagencypr@gmail.com` (correcto), todo el uso de Resend es condicional (brief/alert/oracle/aria) → nada que reportar = no se llama a Resend. **Fix (sesión futura · chico):** cambiar la condición a **brief diario INCONDICIONAL** (heartbeat "SENTINEL 97/100 · 0 issues · HERMES sin fallos · todo en orden") → restaura la comunicación oficial diaria + el resumen HERMES viaja gratis. **NO arreglar canal · cambiar la condición.** Nota: la notificación HERMES (`f58a416`) NO depende de esto — el nivel 2 (alerta inmediata crítica) llama a Resend DIRECTO, independiente del brief.

## 🟡 DEBT-TELEGRAM-CHANNEL (21 jun · canal oficial adicional · NO urgente)

Telegram como 2do canal oficial de notificación (redundancia al email). **El código ya lo soporta** (`alert_dispatcher._send_telegram` + `dispatch_hermes_alert` lo invocan · off mientras no haya credenciales). Falta: pegar `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` en Railway (el restart re-lee settings · sin code deploy) → se activa solo. Útil porque si Resend cae, Telegram entrega igual (cubre el blind-spot del canal email-único).

---

## 🟢 DEBT-ANALYTICS-OAUTH-PER-CLIENT (Google ✅ CERRADO 23 jun · Meta-analytics RETIRADO → DEBT-...-META OBSOLETA)

El connect de analíticas (OAuth Meta/Google · `/oauth/{meta,google}/authorize` → `oauth_tokens`) es **per-USUARIO + esqueleto** (503 en prod · faltan `META_APP_ID/SECRET` + `GOOGLE_CLIENT_*` · `oauth_tokens` vacía). Por eso NO se pudo mover a "Cuentas Sociales" (per-negocio) en la consolidación de botones (21 jun): los hooks `useMetaOAuth`/`useGoogleConnect` no aceptan `client_id` (el backend lo deriva del usuario). **Decisión:** el connect de analíticas **se reconstruye DENTRO del arco Analytics**, ahí nace **per-negocio en su lugar único** (Cuentas Sociales). Para vivir per-negocio necesita: (1) backend que `/oauth/{meta,google}/authorize` acepte `client_id` (escribir `oauth_tokens.client_id` del negocio activo · un reseller con 4 negocios conecta Meta para Mail Boxes sin pisar otro); (2) cablear el OAuth real + creds en Railway; (3) el botón per-negocio en Cuentas Sociales + el consumo (Centro de Inteligencia/Analytics ya consume-only, apuntan ahí). Hoy: los hooks `useMetaOAuth`/`useGoogleOAuth` quedan reservados (sin uso) para ese arco; los componentes per-usuario `ConnectMeta/GoogleButton` + `SocialAccountsSection` se borraron (dead code).

**CERRADO (Google · 23 jun · `b5e8a10` en prod):** `/oauth/google/authorize`+`/status` reciben `client_id` del Switcher (query requerido) y validan ownership vía `resolve_client_or_403` (= `get_client` + `user_owns_client`, el **MISMO** ownership que `chips.py` que consume el mismo token Google). `callback` ya era correcto (client_id del state firmado · solo authorize+status tenían el gap). 5 tests (corazón = ajeno→403 en authorize Y status · parchean deps del resolver → 403/404 real = aislamiento probado) · gate 15/15 · line-neutral. ✅ **DEBT-ANALYTICS-OAUTH-PER-CLIENT-META → CERRADA y luego OBSOLETA:** se cerró en código (`955a558` · `meta_oauth.py` pasó a `resolve_client_or_403`) aunque este doc la daba "abierta" (texto **stale** · contradicción doc↔código) · y el 23 jun Meta-analytics fue **RETIRADO completo** (`2b6f189`/`c91fd4e` · `meta_oauth.py`/`_meta_insights.py` borrados) → el connect de Meta insights ya no existe. Inteligencia y la sección Analítica quedan **solo Google**.

---

## 🟡 DEBT-PLATFORMS-PINTEREST-SNAPCHAT-THREADS-BLUESKY (21 jun · tab Cuentas · NO urgente)

Nace en el **arco Reddit + tab Cuentas honesto** (5 commits `08a87b8`→`edd5955` · gate pendiente del push del conjunto). El tab Cuentas de ARIA (`ClientSocialAccounts.tsx` · NO el modal §7) ofrece **7 redes conectables**: IG/FB/TikTok/X-Twitter/LinkedIn/YouTube + **Reddit** (agregado este arco · Zernio da authUrl · `get_connect_url` es genérico · migr `00071` amplió el CHECK 6→7). Cuatro quedan **"Próximamente"** (texto gris, sin botón, debajo del picker · NO accionables): **Threads, Bluesky** (Zernio sin authUrl prioritario) · **Pinterest** (Zernio `/connect/pinterest` = **503**, caída temporal) · **Snapchat** (**403**, beta). NO se insertan en `social_accounts` → **no necesitan estar en el CHECK todavía**.

**GATILLO de habilitación:** cuando Zernio devuelva **200 + authUrl** para pinterest/snapchat (re-sondear `GET /connect/<platform>?profileId=<real>` · para threads/bluesky: confirmar prioridad de producto), habilitar la red con la receta de abajo.

**RECETA de 3 capas (actualizar las TRES juntas — o el guard falla, que es lo deseado):**
1. **CHECK (DB):** nueva migración que `DROP`+`ADD` el CHECK de `social_accounts.platform` con la red nueva (patrón `00071`). Dry-run read-only antes (0 filas en conflicto) · aplicar a Supabase **ANTES** del front (regla de orden de deploy · ventana de insert-rechazado = bug en vivo).
2. **Constante conectable (front):** mover la red de `COMING_SOON_PLATFORMS` → `CONNECTABLE_PLATFORMS` en `src/lib/social-platforms-tab.ts` (fuente única) + actualizar `TAB_PLATFORMS_LEGEND`.
3. **Lista coming-soon (front):** es la MISMA constante — el "movimiento" de una lista a la otra en `social-platforms-tab.ts` cubre capas 2 y 3 a la vez (por eso es fuente única).

**GUARD YA ACTIVO** (`src/test/socialPlatformsCheckSync.test.ts`): ata capa 1 ↔ capa 2 — lee el `CHECK (platform IN (...))` de la migración `00071` **de disco** y lo compara contra `CONNECTABLE_PLATFORMS`. **Si habilitás una red en la constante sin tocar el CHECK (o viceversa), el test FALLA.** Eso es bueno: impone a la máquina actualizar las 3 capas juntas (no depende del docstring). **OJO al agregar una migración nueva:** el test hoy hardcodea `startsWith("00071")`; al sumar la red en `000NN`, hay que apuntar el test a la última migración con CHECK platform (o generalizarlo a "la última") — si no, comparará contra el CHECK viejo (7) y fallará aunque la DB esté bien.

**Icono:** redes sin brand-icon en Lucide caen a `Globe` (fallback de `getNetworkIcon`) — aceptable para coming-soon; al habilitar, evaluar icono propio. **whatsapp/telegram FUERA** de este arco (otros flujos · DEBT-092 / DEBT-TELEGRAM-CHANNEL).

---

## ✅ DEBT-HEALTH-FALSE-GREEN (21 jun · `/health` honesto · FG1/2/3 RESUELTOS · `/status` nota)

El `/health` reportaba **`"37/37 agents healthy"` sintético** — 3 false-greens (familia del SENTINEL "siempre OK" y del 28): **FG1** `status:"healthy"` literal hardcodeado (hasta el camino `except` lo devolvía) · **FG2** `total_agents = count if count else 37` + `except: 37` → DB caída reportaba **37** igual (y `else 37` enmascaraba un 0 real) · **FG3** `agents:"37/37"` = `count/count` (tautología que finge fracción vivos/totales). **FIX:** `get_stats.count_active_agents()` devuelve **`None` on failure** (NO reusa `_safe_count` que da 0 → reintroduciría FG2) · `get_stats.build_health()` deriva el status del conteo real (healthy solo con conteo>0 · None→`degraded:agents_count_unavailable` · 0→`degraded:no_active_agents`) · campo honesto `agents_active:int` (sin N/N) · `git_sha`/`environment` conservados (ya honestos) · root `/` también limpiado (su gemelo FG2/FG3). 7 tests (3 ramas + blindaje anti-regresión: jamás "N/N", jamás 37, status≠siempre-healthy). Consumidores verificados read-only: nadie parsea `agents:"N/N"` (el SENTINEL network-worker solo mira headers/status del `/health` · los hooks del front leen la TABLA agents) → shape segura de cambiar.

**NOTA `/api/v1/status` (cosmético · NO se tocó · candidato observabilidad):** devuelve `status:"operational"` como **constante sin probe detrás** — no enmascara un check que falle (a diferencia de FG1/2/3 que SÍ mentían salud cuando algo se rompe), es "la API respondió" por construcción. **No agrandar el commit con un probe nuevo.** Cuando se toque observabilidad, derivarlo de un ping real (DB/deps). Hermano de [[gate-pytest-false-green]] / DEBT-VERCEL-NO-TSC-CHECK.

---

## ✅ ARCO 1 · PIPELINE HISTÓRICO — `social_metrics` EN PROD (22 jun · cimiento de LUAN)
**HECHO (prod · verif 6/6):** tabla `social_metrics` (migr 00072 · `63a617c`) + cron diario 6am AST=10:00 UTC `social_metrics_snapshot` (`b6efc01` · cron 26→27 · el scheduler corre en AST). Familia 1 = Zernio social organic. **Verif viva:** 80 filas reales (MB 11·OR 10·Wudi 1·Zafacones 58) · aislado por client_id (MB sin filas de OR) · valores==Zernio (MB IG reach per-día suma 155 · OR 11) · NULLs honestos (FB reach0=0-REAL · snapshot-row activity NULL · activity-row followers NULL) · idempotente (RUN2=80, cero dup).
**Diseño:** per-día actividad (Zernio la da real · NO resta) + snapshot followers (diff entre snapshots) · `UNIQUE(client_id,platform,metric_date)`+profile_id traza · RLS verbatim social_accounts · NULLABLE (NULL=no-dato, nunca 0) · best-effort por negocio.
**Forward-compat:** familias 2 (ads→`ads_metrics`) y 3 (web/SEO→`web_metrics`) = tablas hermanas TIPADAS futuras (NO jsonb) · `social_metrics` intacta al sumarlas. Cubre parcialmente DEBT-MCP-ANALYTICS (familia 1; 2/3 futuras).
**SOLO-ESCRITURA:** el panel sigue live-read · LUAN no razona sobre el histórico aún (futuro).
**PENDIENTE (no bloqueante):** (a) `/system/cron-status`=27 en vivo (owner-only · evidencia indirecta: app healthy=lifespan corrió 27 add_job). (b) MAÑANA: cron automático 6am (filas nuevas metric_date=mañana · hoy fue manual).
→ Cierra gap "Zernio sin ventana" · REQUISITO de LUAN. **ORDEN restante:** Arco 2 (web/SEO directo · GA4/GSC coded · falta connect OAuth per-negocio + creds Railway · DEBT-ANALYTICS-OAUTH-PER-CLIENT) → Arco 3 LUAN (ads · `zernio_ads_adapter` en cero) → Arco 4 Centro cableado + comunicación REX↔LUAN↔NOVA↔Analytics.

---

## 🟢 ARCO 2 · CONNECT GOOGLE (INSIGHTS) — CERRADO 23 jun · **DECISIÓN EJECUTADA: Meta-analytics RETIRADO (duplicaba Zernio · queda solo Google) + GA4 Vía A cerrado (picker)** · 4 commits `2b6f189`→`ab62914`

> ✅ **RESUELTA (23 jun):** la decisión fue **RETIRAR Meta-analytics** (duplicaba lo que Zernio ya entrega) + cerrar el gap **GA4 por Vía A** (picker de propiedad). Ejecutado en 4 commits (`2b6f189`→`ab62914` · gate 15/15 c/u). El texto de abajo es el **planteo original (histórico)**.
>
> **PRÓXIMA SESIÓN = UNA SOLA TAREA (read-only · sin tocar código):** El connect Google+Meta del Arco 2 (`b5e8a10`/`955a558`/`7fee529`/`5aa8f62`/`d695abc`, en prod) se construyó para **INSIGHTS (leer métricas)**, pero el owner siempre quiso **ADS (gestión de campañas = Arco 3/LUAN)**. Preocupación genuina: ¿es código **duplicado/muerto** frente al Arco 3? ¿el connect de **Meta insights** solapa con un futuro **Meta Ads**? ¿la **tab Meta del Centro de Inteligencia** queda redundante? **Analizar A FONDO contra el código real** (no opinión rápida) → **entregar una decisión fundamentada con evidencia: mantener / retirar parte / refactor**, y esperar review del owner ANTES de cualquier otro paso. **🔒 REGLA INVIOLABLE: cero confiarse de una sola línea · cada afirmación verificada contra el código · lo no confirmable = "NO CONFIRMADO"** (existe por el error §3.1: confiarse de una línea de un doc sin verificar · NO se repite). **NO** investigar plataformas de ads, **NO** recon Zernio, **NO** escribir docs, **NO** tocar código — solo la decisión del Arco 2. *Contexto para decidir (no verificado · NO asumir): Arco 3 sería página DEDICADA de gestión de ads (gestionar≠mostrar) · Meta saldría de Inteligencia (quedaría solo Google) · ads = conexiones SEPARADAS por plataforma (la captura lo muestra · el doc §3.1 "cuentas ya conectadas sirven" era FALSO · key compartida ≠ conexión de cuenta compartida).*

### (histórico) ARCO 2 · FUENTES WEB/SEO DIRECTO (GA4+GSC) — PUNTO DE CONTINUACIÓN (23 jun · **Fase A ✅ CERRADA en prod `b5e8a10`** · código completo A+B1+B2+B3a+B3b en `d695abc`)

**Contradicción CENTRO vs ZERNIO_LUAN resuelta con sonda:** social + ads-de-redes → Zernio · **web/SEO (GA4 sesiones + GSC clicks/impresiones/posición) → DIRECTO** (Zernio no cubre web).

**YA HECHO (sonda 23 jun · read-only):**
- ✅ `GOOGLE_CLIENT_ID/SECRET` presentes en Railway (creds cargadas · el bloqueo "crear creds en Google Cloud" NO aplica).
- ✅ `_google_insights.py` **completo** (GA4 `runReport` sessions + GSC `searchanalytics` clicks/impresiones · real · sin stubs).
- ✅ OAuth backend **per-client** (`google_oauth.py` authorize+callback · state HMAC firma el client_id · CSRF-safe · `_oauth_token_repository` upsert por `(client_id, provider)`).
- ✅ `oauth_tokens` (migr 00037 · per-client) existe · **VACÍA** (nadie conectó aún).

**FALTA (plan por FASES · como Arco 1):**
- **Fase A — CÓDIGO ✅ CERRADA (`b5e8a10` · en prod):** `/google/authorize`+`/status` reciben `client_id` del **Switcher** (query requerido) + ownership vía `resolve_client_or_403` (`get_client`+`user_owns_client` · MISMO ownership que `chips.py`, el sibling que CONSUME el mismo token Google) en vez de `find_client_for_user`. `callback` intacto. **5 tests** (corazón = authorize/status ajeno→403 · aislamiento real · + authorize_propio firma ESE client_id) · gate 15/15 · line-neutral. → **DEBT-ANALYTICS-OAUTH-PER-CLIENT CERRADO** (Meta queda en DEBT-...-META).
- **Fase B — CÓDIGO (PRÓXIMA SESIÓN ARRANCA ACÁ):** **OBLIGATORIO primero:** el hook `useGoogleOAuth.ts` llama `authorize`/`status` SIN `client_id` → con `Query(...)` requerido (Fase A) da **422** · cero impacto hoy (0 tokens · ninguna UI lo monta) · **DEBE pasarle el `activeBusinessId` del Switcher**. Luego: UI nueva en Cuentas Sociales — **SECCIÓN SEPARADA debajo de las redes sociales** con **LEYENDA (pedido explícito del owner):** ARRIBA = redes sociales (orgánico IG/FB/TikTok) · ABAJO = Meta/Google y demás para **ADS y ANALYTICS WEB** (qué conecta cada una, para qué, por qué). Botón "Conectar Google" estilo Zernio (usa `useGoogleOAuth`) + el consumo en el panel/chip Google.
- **Fase C — CONFIG (OWNER · 5 min):** `OAUTH_REDIRECT_BASE` en Railway → **domain-only** (`https://omega-production-3c67.up.railway.app` · hoy malformado full-path → redirect_uri doble) + registrar `https://omega-production-3c67.up.railway.app/api/v1/oauth/google/callback` en Google Cloud Console (Authorized redirect URIs).
- **Fase D — END-TO-END (OWNER):** conectar una cuenta **GA4/GSC real** de un negocio (MB/OR/Milagrosa) → token cae en `oauth_tokens` → el panel muestra datos web reales. **PENDIENTE: ¿qué negocio tiene GA4/GSC para conectar?**

**Honestidad:** A+B (código) se dejan listos+probados · el "funcionando end-to-end" se cierra con C (config Google Cloud) + D (conectar cuenta real) = pasos del owner, no código.

---

## 🟡 DEBT-LUAN-JERARQUIA-ROL (22 jun · decisión owner pendiente · NO resolver ahora)
Tensión sin resolver: LUAN ¿agente vertical con persona propia que reporta a NOVA (visión) o ROL de STRATEGY (canon `OMEGA_ROLES_CANONICO.md` L144/L202-203 · anti-inflación AS-R4)? Opciones: (1) rol vertical de STRATEGY · (2) agente #9 (excepción AS-R4). **Conecta con lo SAGRADO:** "NOVA debe saber de LUAN" toca `persona_nova.py` (SHA1 · ritual X2/G2 + firma owner) — que HOY dice "Coordinas 37 agentes" (**DEBT-ROLES-001** · número falso) + auto-descripción desalineada del canon · y `scripts/verify-personas.sh` NO existe (**DEBT-ROLES-002** · personas no enforzadas). Cableado LUAN→STRATEGY→NOVA + fix del "37" = tarea sagrada del arco LUAN (misma tarea). Detalle en `ZERNIO_LUAN_REFERENCE.md` §3.11. **Nada se toca ahora.**

---

## 📊 ARCO ANALYTICS "PARIDAD DE VERDAD" (21 jun · EN PROD `e5d0f37` · **CERRADO 22 jun** — panel ampliado + chip + /health honesto · DEBT-034 resuelta · bug "28" cerrado · ver header)

**EN PROD (`e5d0f37`):** el fix "Paridad de Verdad" está pusheado. El bug **"28 seguidores falsos"** (violación P1: leer `page_follows.total`=26 de ventana como seguidores actuales) está **RESUELTO** — eliminado `page_follows` (su raíz), test anti-28 con `page_follows.total=26` → total=**5≠28**. **DEBT-034 avanzada, NO cerrada** (ver bug abierto abajo).

**3 commits (gate 15/15 c/u · identidad raisenomega):**
- `c811e55` backend honesto: seguidores=`/accounts.followersCount` (snapshot · NUNCA page_follows), posts reales, best_hour derivado, engagement por red, sin %.
- `973f1ba` frontend: KPIs reales, hardcode "19:00–21:00" eliminado, Engagement % removido, labels "del período", dataDelay.
- `e5d0f37` **limpieza P1**: borrado `analytics_agent.py` sintético (`_get_dashboard_data`=12500/4.2 · `_analyze_metrics` followers=1000) + **6 endpoints huérfanos** de `analytics/router.py`. Conservado `_generate_insights` (uso real content-lab · verificado limpio). `POST /analytics/dashboard-data` → **404**. `GET /dashboard/` (Supabase real) **intacto**.

**Regla GLOBAL nueva fijada (ver SOT §3 P1+):** cero datos sintéticos/mock/placeholder/hardcode · P1 duro end-to-end · vacío honesto (—/empty state) SIEMPRE antes que relleno. **Regla de arquitectura (SOT §3 P6):** resolución uniforme per-negocio · negocio nuevo nace sano · raíz no se parchea 2 veces.

### 🟢 DEBT-ANALYTICS-RESOLVER-PROFILEID · FIX DE RAÍZ EN CURSO (A en prod · B+C local · ver SOT §6)
El resolver pedía followers/posts por **bound_ids** (`social_accounts.zernio_account_id`) — frágil y **vacío en 3 de 4 negocios**. La data vive bajo **`profileId`** (sólido · lo usa engagement). **Síntoma:** Omega Raisen (`5a323aa3`) mostraba —/0 con 5 fol + 7 posts reales · Milagrosa (`9d178128`) sin `zernio_profile_id`. **Causa raíz:** el binding per-cuenta se escribía UNA (client,platform) por vez vía callback OAuth per-red → quedaba incompleto. **FIX DE RAÍZ (3 piezas = 1 solución · una rutina sirve para conectar nuevos Y sanar viejos):**
- **(A) Analytics por profileId** — `f01e238` EN PROD + VERIFICADO EN VIVO (Mail Boxes 5, Omega Raisen "—"→**5**, mejor hora per-negocio real). Uniforme · no depende de bound_ids.
- **(B) `derive_bindings_from_profile`** (commit `afd300a` LOCAL) — deriva TODOS los bindings desde el profileId · `_upsert_binding` extraído (idempotente · 3 callers intactos) · enganche best-effort en `zernio_callback` → negocio nuevo no nace con binding vacío. 5 tests shape real.
- **(C) Backfill Omega Raisen EJECUTADO 21 jun** (misma rutina de B · B==C) — `derive_bindings_from_profile('5a323aa3-f490-40c6-8c5c-443b0fc1b566', '6a32fe37…')` escribió **4 UPDATEs scopeados al client_id exacto** (FB `6a330053…` · IG `6a32fefb…` · LinkedIn `6a3300f0…` · TikTok `6a330159…` → `oauth=connected`). **Twitter intacto (None · Zernio no tiene esa cuenta).** **Idempotencia VERIFICADA EN PROD:** 2da corrida = 4 updates, mismas 5 filas, cero duplicados, Twitter sin tocar. Desbloquea **PUBLICAR** (REX usa `zernio_account_id`) · analytics ya andaba por profileId.
**Pendiente:** Milagrosa entra por (B) cuando el owner la conecte (sin profile en Zernio · no se puede backfillear · test vivo del onboarding sano). Push de B+C tras revisión del owner.

### 📋 Pendientes registrados (post-fix de raíz · no deuda silenciosa)
- **Posts KPI REMOVIDO (21 jun · opción 3 · honesto):** la API REST de Zernio **no expone la ventana "this period"** — el 5 (Mail Boxes) / 7 (Omega Raisen) vive SOLO en el panel UI. Sondeado: `externalPostCount` da 5/**0** (0 con 7 posts reales en Omega Raisen, no sincronizado) · `daily-metrics.postCount` sin ventana da **10**/7 (platform-posts de toda la historia · Mail Boxes ≠ 5) · **7 date-params probados** (`days`/`period`/`from-to`/`startDate`/`endDate`/`dateRange`/`range`) **todos ignorados**. Mismo patrón que el ER por-post 1.66% (número de panel, no de API). Reproducirlo = mini-28 → prohibido (regla global P1). **Reintroducir cuando se halle endpoint con ventana real.** Coherente con haber quitado Engagement % por lo mismo.
- **UI (con el panel ampliado):** quitar mención "Zernio" del aviso de retraso (proveedor invisible) · quitar selector "Todos los clientes" (redundante) · compactar "Mejores horas para publicar".
- **Métricas nuevas a evaluar (confirmar API REST primero · no solo el panel Zernio):** Total reach, Engagement rate, Engagement over time, Top Performing Posts, Platform Breakdown.
- **Reconciliación FB:** Zernio reporta `followersCount`=3 para FB Mail Boxes vs 1 recordado por owner → pendiente verificación contra facebook.com directo.
- **Serie temporal FB/TikTok en GrowthChart** (hoy solo IG · el total ya suma las 3).

---

## ✅ B-2 FACEBOOK HEADLESS — CERRADO END-TO-END + AISLAMIENTO VERIFICADO CON DATOS (19 jun)

**El connect headless de redes está CERRADO en las dos plataformas: IG (18 jun) + FB (19 jun).** Una página
de un negocio cae en SU profile Zernio y en ningún otro (aislamiento white-label = el corazón del arco),
**probado con datos**: conecté una FB de prueba (Wudi App) a Mail Boxes → cayó verde en SU profile, ausente
del de Omega Raisen, y las 4 cuentas de Omega Raisen intactas. Teardown hecho (Wudi App desconectada · DELETE
200 · Mail Boxes queda solo con IG mail_bd, limpio para la cuenta FB real).

**AISLAMIENTO (read-only `GET /accounts?profileId` · post-teardown):** Mail Boxes (`6a3302c498…`) = `instagram
mail_bd` (1) · Omega Raisen (`6a32fe37aa…`) = facebook "Raisen Omega Agency" + IG raisenagency + LinkedIn +
TikTok (4, intactas). La FB de prueba NO se filtró a Omega Raisen. ✓

**DOS bugs reales destapados y cerrados en este cierre (lecciones de método):**
1. **`noopener` mató el relay (latente desde IG).** `window.open(..., "noopener")` deja `window.opener=null`
   → el relay `window.opener.postMessage` de `/zernio/return` era un **NO-OP** → el page-picker FB nunca abría
   Y el auto-verde de IG nunca funcionó por postMessage (el verde de IG llegaba por refetch al navegar/recargar
   — `DEBT-ZERNIO-AUTOVERDE-LATENCIA` mal diagnosticada como latencia). **Fix: relay por BroadcastChannel
   same-origin (sobrevive noopener) + fallback storage · `noopener` mantenido (anti-tabnabbing).** Commit
   `df1a272` (front · ZernioReturn + ClientSocialAccounts + test). El owner aportó el dato clave ("yo nunca usé
   Verificar") que reveló el alcance real del bug.
2. **El contrato del adapter estaba MAL INFERIDO (endpoints inexistentes).** El adapter pegaba a
   `/connect/get-facebook-pages` y `/connect/update-facebook-page` → **0 matches en el OpenAPI de Zernio**. El
   400 "Profile ID is required" era pista engañosa de un path muerto (por eso el tanteo capa-por-capa no
   convergía). **Corregido contra el OpenAPI real** (`docs.zernio.com`) · commit **`910756f`**: un solo path
   **`/connect/facebook/select-page`** (GET lista · POST elige) · param **`tempToken`** (no `accountId`) ·
   **`userProfile`** requerido en el POST (capturado del callback con parseo defensivo · malformado/ausente →
   None, no crashea, no se loguea = PII) · respuesta **`account.accountId`** (no `_id`). **Lección: con 2 E2E
   fallando sin converger, el problema es una premisa, no un param — ir a la doc autoritativa cortó el tanteo.**

**EN PROD (todo pusheado · gate 15/15 c/commit):** `df1a272` (BroadcastChannel) · `1d8cf61` (profileId,
intermedio) · `910756f` (contrato real · el que cerró el E2E). Frontend (Vercel): BroadcastChannel + page-picker
vivos. Backend (Railway `910756f`): adapter + stash + callback + endpoints `/facebook/pending-pages` +
`/facebook/select-page`.

**DEUDAS ABIERTAS (registradas · ninguna bloquea el cierre):**
- **`DEBT-ZERNIO-TOKENS-IN-ACCESS-LOG`** (prioridad MEDIA-ALTA): el access-log de uvicorn imprime la URL
  completa del callback → los Graph tokens `EAA…` + `connect_token` quedan en claro en los logs de Railway. El
  diseño headless sacó los tokens del navegador pero NO del server-log. Mitigación: callback por POST/fragment,
  o sanitizar el access-log de esa ruta.
- **`DEBT-FB-STASH-MULTIWORKER`**: el stash in-memory asume `--workers 1`. Multi-worker rompería (un worker
  stashea, otro atiende el fetch). Alternativa al escalar: fila DB efímera.
- **`DEBT-FB-STATE-5SEG-CLEANUP`**: `verify_state` tolera states de 5-seg (legacy pre-user_id). Quitar la
  tolerancia cuando no queden states viejos en vuelo.
- **`DEBT-FB-RETRY-TRANSIENT`**: `select-page` hace `clear_pending` en `finally` → un transitorio de Zernio
  obliga a rehacer el OAuth completo. Para 422-real está bien; para transitorio es agresivo. Diferenciar si los
  transitorios resultan frecuentes.

**PENDIENTES owner-side (NO Claude):** revocar "Social Media Connector" en Wudi App (mata el `EAA…` expuesto en
el access-log) · rotar el JWT `reseller@omega.com` (`61f88b91`) · borrar historial de chats con JWTs.

**REGLAS del arco (para futuros cambios de redes):** no `persona_*`/`limits_omega`; identidad raisenomega; gate
15/15 + test-first; un commit por paso + review del owner antes del push; el verde SIEMPRE de connected-accounts
(verdad Zernio), nunca de un postMessage/canal/select; cero publish; NO `META_APP_*` (ruta Zernio ≠ Meta-directa).

### RECON plataformas restantes (19 jun · read-only · NADA construido · OpenAPI Zernio real)

Dos patrones connect headless (spec `/connect/{platform}`): **A-directo** (redirect trae `accountId` → callback
lo persiste genéricamente · cero código por plataforma) vs **B-selección** (redirect trae OAuth data → endpoint
`/connect/<plat>/select-*`). OMEGA expone 6 redes.

| Red | Patrón | Estado |
|---|---|---|
| instagram | A directo | ✅ cerrado (real, aislado) |
| facebook | B `select-page` | ✅ cerrado (real, aislado) |
| tiktok | A directo | ✅ **SÓLIDO** — connect + **publish E2E** + aislamiento probados con datos (ver §TikTok PUBLISH abajo) |
| twitter/X | A directo | ⚪ connect-url 401 (montado, paridad) · **debería conectar sin código** · solo E2E |
| youtube | A directo | ⚪ idem · caveat Google multi-channel (probar cuenta de 1 canal) · solo E2E |
| linkedin | B `select-organization` | 🔶 hosted viejo en OR · headless NO construido · **sub-patrón DISTINTO a FB** |

**DIFERIDOS a sesión dedicada propia (NO construir hasta GO explícito):**
- **Twitter/X + YouTube** — Patrón A · cero código esperado · **solo E2E** con cuentas de prueba en profile
  **DESCARTABLE** (NO Mail Boxes, que es producción) · YouTube probar primero con cuenta de 1 solo canal.
- **LinkedIn** — Patrón B pero **NO copiar el branch de FB a ciegas**: usa `pendingDataToken` (lista de orgs muy
  grande para la URL) → `GET /connect/pending-data?token=` devuelve tempToken+userProfile+organizations →
  `POST /connect/linkedin/select-organization {profileId,tempToken,userProfile,accountType,selectedOrganization}`
  con `accountType` personal/organization (org-picker). Arco de construcción propio con review paso a paso.
- Otras vía Zernio (fuera del PLATFORMS actual): googlebusiness/pinterest/snapchat/whatsapp = paso intermedio;
  threads/reddit/bluesky/telegram/discord = directas.

**TikTok publicación (recon · vivo en repo HOY):** pipeline genérico `zernio_adapter.create_post` (POST `/posts`
· `platforms:[{platform,accountId}]` + `mediaItems:[{url,type}]` + publishNow) + ruta `POST /api/v1/publish/auto`
+ `_publish_service.publish_scheduled_post`. **Cadena connect→publish CABLEADA y verificada con datos:** publish
resuelve el accountId vía `get_zernio_account_id`(social_accounts) → `resolve_account_id` (binding per-negocio o
falla honesto · sin adivinar) → `create_post`. TikTok ∈ `_MEDIA_REQUIRED` (exige video). Solo `status='pending'`
(humano aprobó) publica. **Token TikTok 24h: lo maneja ZERNIO** (no mandamos token · pasamos accountId · Zernio
publica con su conexión guardada · si el token venció y Zernio no lo refrescó → non-2xx → fallo honesto).

### ✅ REX · Publicador Autónomo (DEBT-098 F1) — DESPLEGADO E INERTE en prod (20 jun · 7331476 · 00069 aplicada)

Primer incremento de REX construido entero, desplegado y **verificado inerte con datos**. REX = rol ejecutor
(NO 9no agente · `canonical_agents` intacto · `operational_count()==8`): cron cada 5 min recorre `scheduled_posts`
`pending` con `scheduled_for<=now()` y publica lo que el humano YA aprobó, tras un gate determinístico de 7 checks.

**Piezas (6 commits `5c3435d`→`7331476`):** F0 migración `00069` (`clients.rex_addon_active`/`autonomous_mode_on`/
`crisis_active` + `rex_publish_log` append-only · RLS espejo 00027) · F1 `rex_gate.py` puro (7 checks orden prioridad:
gating→crisis→brand_voice≥0.7→confidence≥7→posts<3→media→connection · umbrales de LIMITS_OMEGA/X5, cero hardcode) ·
F2 UC flag-agnóstico + **wrapper `rex_publish_fn`** que lee `REX_LIVE_ENABLED` (default OFF=shadow · `publish_scheduled_post`
INALCANZABLE en OFF) + repo/steps · worker `rex_publisher_worker` (subclase BaseWorker · filtra add-on AND toggle) +
cron 25º (`*/5`·`max_instances=1`·grace 300) + billing flip (`publisher_*`→`rex_addon_active`, NO toca el toggle · cancela=apaga
ambos) + toggle UI Calendar (Bot Lucide · visible solo si compró · off default · PATCH con `resolve_client_or_403`).

**Garantías (probadas con código + datos):** flag leído POR-CORRIDA (kill-switch sin reinicio) · filtro exige addon AND
toggle (2 capas) · default OFF en la migración · ownership en el PATCH. **Inercia doble en prod:** `REX_LIVE_ENABLED`
sin setear (shadow) + universo addon+toggle=**0** + `rex_publish_log` vacío (0 real). 41 tests · gate 15/15 cada fase ·
persona/limits SHA1 intactos. **PENDIENTE: E2E en cuenta descartable** (enciende `REX_LIVE_ENABLED` · paso con GO aparte ·
guion en `REX_E2E_CHECKLIST.md`) → luego activación gradual por cliente real. cron-status=25 y env de Railway: verificación del owner (endpoint authed / panel).

### ✅ TikTok PUBLISH end-to-end — SÓLIDO (19 jun · probado con datos · entorno descartable)

TikTok pasó de "funciona" a **SÓLIDO**: connect + **publish end-to-end** + aislamiento, los tres probados con
datos. E2E real: video de prueba salió en la cuenta **wudy245 (PRUEBA)**, el **binding per-negocio resolvió la
cuenta correcta** (`get_zernio_account_id`→`6a35c8b5`, NO la real de Mail Boxes `6a35b546`), `scheduled_post`
`status=published` + `platform_post_id` real (`6a35ce76`), **token-24h alcanzó** (Zernio publicó con la conexión
de hoy), **Mail Boxes/Omega Raisen intactos** (cero contaminación), **teardown limpio** (cero residuo verificado:
sin wudi/wudy/OMEGA_EXP en profiles/accounts/DB).

**GOTCHA reusable — TikTok NO borra posts vía API:** Zernio responde literal *"TikTok does not support post
deletion via API. Please delete the post manually from TikTok."* (DELETE `/v1/posts/{id}` y POST `/unpublish`
ambos → 400). **Todo E2E de publish en TikTok deja un video que SOLO se quita manual desde la app** → planificar
el teardown con eso (borrar el video a mano ANTES de desconectar la cuenta · el resto sí es API).

**PATRÓN reusable del E2E de publish descartable** (para futuros publish-tests de cualquier plataforma · el
publish es **CLIENT-céntrico**, necesita un cliente OMEGA, no solo un profile Zernio): (1) **cliente OMEGA
descartable** + cuenta de prueba conectada vía UI → profile Zernio auto-creado + binding `social_accounts`
escrito; (2) materializar el draft de la Cola como `scheduled_post` `pending` (client_id + social_account_id +
content_id + media_url); (3) **ÚLTIMA PUERTA read-only ANTES del disparo:** la query exacta del resolver
(`get_zernio_account_id(client, platform)`) confirma que resuelve la cuenta de PRUEBA, NO la real — si resuelve
algo real → PARAR; (4) verificar read-only que NO hay cron de auto-publish (toda la cadena dispara solo por
`POST /publish/auto`) + auto-accept UI OFF; (5) **publish gateado por GO manual del owner**; (6) verificar
`platform_post_id` real + cuenta correcta; (7) **teardown completo** (video manual en TikTok + DELETE
account/profile + DELETE DB rows en orden FK + DELETE MP4 storage + verif cero residuo).

**Remanente inofensivo:** el *record* del post `6a35ce76` queda huérfano en Zernio (no borrable por API · video ya
borrado manual · su cuenta/profile/cliente eliminados · fuera de todo profile · sin efecto).

---

## 🟢 HANDOFF · B-2 ZERNIO HEADLESS · MIGRACIÓN COMPLETA + E2E VERDE (18 jun · RETOMAR ACÁ)

**QUÉ SE LOGRÓ:** el connect de redes migró de **hosted → headless** y el bug de aislamiento
(`DEBT-ZERNIO-MAILBOXES-NO-ATTACH`) está **CERRADO end-to-end y verificado en vivo**: una cuenta de un
negocio B se adjunta a SU profile Zernio y cae verde, **aislada** del profile de otro negocio.

**COMMITS EN PROD (todos en `main` · git_sha `fe68a28`):**
- `22bc542` Commit 1 · backend headless: connect-url firma `state` (HMAC) + callback `GET /clients/zernio/callback` (sin JWT · verify firma → 400 · exige `profileId==client.zernio_profile_id` aislamiento · persist hardened 422-sin-guardar · FB `step=select_page` GATED) + `_zernio_persist.py` (hardening compartido con zernio-sync).
- `4386171` Commit 2 · frontend: ruta `/zernio/return` (relay · postMessage+close · NO pinta verde) + listener en `ClientSocialAccounts` (solo dispara `refetchConnected` · verde sale de connected-accounts = verdad Zernio) + botón honesto intacto.
- `ac231c1` Commit 2.1 · origen firmado en el state (base64url) + `_front_base` valida contra allowlist (anti open-redirect · test `evil.example`) → el popup vuelve al MISMO origen del user (www vs non-www).
- `8e67297` Commit 2.2 · `build_callback_url` con `urlparse → scheme://netloc` (descarta path pegado) + **RAISE ruidoso si la base no tiene scheme+host** (en vez de mandar redirectUrl relativo) + tests que LANZAN con base=""/sin-host (cierra el verde-falso del gate).
- `fe68a28` bump **pypdf 4.0.0 → 6.13.3** (cierra `GHSA-jm82-fx9c-mx94` · DoS RAM · APLICABA: 3 sitios parsean PDF no-confiable · API estable verificada · commit aparte).

**CAUSA RAÍZ DEL 500 (resuelta · era CONFIG, no código):** faltaban **DOS env vars en Railway** (nunca seteadas · Google/Meta OAuth jamás usado en prod). El connect headless es el 1er flujo que las usa:
- **`OAUTH_REDIRECT_BASE`** ausente → `build_callback_url` daba redirectUrl relativo → Zernio 400 → 500.
- **`OAUTH_ENCRYPTION_KEY`** ausente → `sign_state` (corre ANTES) → `CryptoNotConfigured` → 500.
**El owner creó AMBAS en Railway** (`OAUTH_REDIRECT_BASE=https://omega-production-3c67.up.railway.app` · `OAUTH_ENCRYPTION_KEY`=secreto aleatorio estable). Tras eso: connect-url verificado **HTTP 200** (curl autenticado cuenta dueña) con el callback ABSOLUTO embebido en el `state` (no `zernio.com/dashboard`). *(Lección: mi 1er probe al callback de Google con state de 1-parte NO ejercía `_signing_key` → falso "key presente"; el probe correcto = state de 3 partes → 503.)*

**E2E IG (owner · 18 jun) — VERDE:** Allow con cuenta descartable `wudi.app` → popup volvió a OMEGA y cerró solo → IG cayó **verde en Mail Boxes** (auto, tras breve latencia). **Aislamiento CONFIRMADO con datos:** `GET /accounts?profileId=MailBoxes` = `wudi.app` ✓ · `profileId=OmegaRaisen` = sus 4 originales, SIN wudi ✓. **Las 4 de Omega Raisen intactas.** ⚠️ Login OMEGA correcto = cuenta DUEÑA `61f88b91` (`reseller@omega.com`); `741ace1c` (`raisenagencypr`) NO es dueña → 403.

**TEARDOWN HECHO:** `wudi.app` desconectada del profile de Mail Boxes (DELETE 200) → **Mail Boxes = 0 cuentas, limpio** para la cuenta REAL · profiles=5 · cero residuo `OMEGA_EXP_*`. (Nota menor: el row de `social_accounts` de MB-instagram puede tener el binding stale de wudi · inofensivo · se sobreescribe en el upsert cuando conecte la cuenta real · no muestra verde porque connected-accounts lee Zernio=0.)

**PENDIENTES:**
- **FB / `step=select_page` — GATED, NO construido.** IG trajo `accountId` directo; FB puede requerir elegir Página. El callback ya redirige `needs_page` honesto (no verde, no roto). **Para construirlo: PRIMERO capturar el contrato FB real** (re-armar el endpoint de captura temporal del experimento ya validado · `DEBT-ZERNIO-CAPTURE-ENDPOINT-TEMP` patrón) — NO a ciegas.
- **`DEBT-ZERNIO-AUTOVERDE-LATENCIA` — MAL DIAGNOSTICADA · RESUELTA por el fix BroadcastChannel (19 jun).** NO era latencia: el `window.open(..., "noopener")` dejaba `window.opener=null` → el `window.opener.postMessage` del relay `/zernio/return` era un **NO-OP** → el auto-verde de IG **NUNCA funcionó por postMessage** (el owner confirmó que jamás tocó "Verificar conexión"; el verde de IG llegaba por otra vía: refetch al navegar/recargar). FB lo destapó (sin fallback, dead-end total). **Fix:** relay por **BroadcastChannel** same-origin (sobrevive noopener) + fallback storage · `noopener` se MANTIENE (anti-tabnabbing). Arregla el picker de FB Y el auto-verde de IG juntos. **PENDIENTE: re-verificar IG tras el fix** (E2E rápido · confirmar que IG cae verde por el canal nuevo, no por la vía vieja).
- **`DEBT-ZERNIO-MULTI-SAME-PLATFORM`** (de antes): upsert por `(client_id, platform)` limit 1 → una cuenta por red por negocio.
- Deuda lateral: `OAUTH_REDIRECT_BASE`/`OAUTH_ENCRYPTION_KEY` faltaban → **Google/Meta Analytics OAuth también estaban rotos**; ahora con las env vars creadas, su state-signing/redirect quedó bien (no usado aún · upside).

**REGLAS:** no `persona_*`/`limits_omega`; identidad raisenomega; gate 15/15 + test-first; FB no se toca sin contrato capturado; cero publish.

---

## 🟢 PASO 0 FB · CONTRATO CAPTURADO + teardown completo (18 jun · cerrado)

**Contrato FB headless CONFIRMADO en vivo** (ya NO es asunción · captura controlada con endpoint temporal):
- `step=select_page` (param exacto "step") · **DOS tokens en el retorno: `tempToken` + `connect_token`** (FB añade `tempToken` vs IG, que solo traía connect_token).
- La **lista de páginas NO viene en el redirect** → se elige **EN el consent de Meta** (Meta lista las páginas, el usuario elige + Guardar).
- El **select se completa server-side con el `tempToken`** (probable `list-facebook-pages` / `get-pending-oauth-data` contra Zernio).
- La página **NO aparece en `GET /accounts?profileId` hasta completar el select** (estado `select_page` = no adjunta a ningún profile).
- Aterriza en **nuestro dominio** (`omega-production-3c67…`) ✓ · consent = **"Social Media Connector" (app de Zernio)** → **NO exige `META_APP_*`** (regla STOP NO disparada · ruta Zernio, no Meta-directa).

**Teardown COMPLETO (igual de limpio que IG):**
- Endpoint de captura removido del repo (commit `8cc1ffc` · `6fabca4` fue el re-arme) · **`/zernio-experiment/capture` da 404 en prod** ✓.
- Profile de prueba `OMEGA_EXP_FB_DELETEME` borrado → **profiles=5, sin residuo `OMEGA_EXP_*`**.
- **Página real "Mail Boxes Design" NUNCA adjuntada** (`select_page` no completado · global facebook = solo `Raisen Omega Agency` de Omega Raisen · **sin leak** · confirmado read-only).
- `"Social Media Connector"` **revocado en Meta** (cuenta Lucas Mark · Activos=0) · `ZERNIO_CAPTURE_TOKEN` **retirado de Railway+.env**.
- **`DEBT-ZERNIO-CAPTURE-ENDPOINT-TEMP` CERRADA** (2da vez · ahora FB).
- Nota: `instagram/mail_bd` está en el profile Mail Boxes (su lugar correcto · binding stale inofensivo · se sobreescribe al conectar la IG real · no se tocó).

## 🔜 PRÓXIMO ARCO — BRANCH FB (NO empezado · construir sobre el contrato capturado)
1. **Adapter Zernio:** `list_facebook_pages(tempToken)` + `select_facebook_page(...)` — **NO existen** (grep `zernio_profiles.py` = 0 matches) · contrato real ahora conocido.
2. **Callback** (`zernio_callback.py:51-53`): en `step=select_page`, en vez de `needs_page` dead-end, **entregar la data pendiente FIRMADA al frontend** para el picker.
3. **Page-picker UI:** lista páginas → usuario elige → llama select → refetch → verde. Botón honesto intacto.
4. **Persist:** tras el select, la página aparece en `/accounts` → `persist_zernio_account` (`_zernio_persist.py:22-45`) la captura por accountId (**reuso** · el paso NUEVO es el select, no el persist).
5. **E2E** con cuenta FB de prueba que **NO administre negocios reales** (lección: "Lucas Mark" administra Zafacones+Mail Boxes reales → usar una cuenta FB limpia tipo `wudi.app` para que el aislamiento del branch salga sin tocar nada real).

**PROGRESO:** Paso 1 ✅ adapter `zernio_facebook.py` (`get_facebook_pages`+`select_facebook_page` · commit `35a302e`) · Paso 2 ✅ stash server-side `_zernio_pending.py` + branch `select_page` en callback (tokens nunca al navegador · key=`(client_id,platform)`). Pasos 3-5 pendientes.

**DEUDA registrada:** `DEBT-FB-STASH-MULTIWORKER` — el stash de tokens FB (`_zernio_pending.py`) es in-memory → asume Railway `--workers 1` (igual que `DEBT-SCHEDULER-SPLIT`). Multi-worker lo rompería (un worker stashea, otro atiende el fetch del paso 3 · no comparten memoria). Alternativa al escalar: fila DB efímera. NO construir con DB ahora (sobre-ingeniería para 1 worker · queda escrito para que no sorprenda).

**DEUDA registrada:** `DEBT-FB-RETRY-TRANSIENT` — `select-page` hace `clear_pending` en `finally` → limpia el stash ante CUALQUIER fallo, incluido un transitorio de Zernio (timeout/5xx). Para un 422-real (página no en el profile) está bien (reintentar no ayuda). Para un transitorio es agresivo: obliga a rehacer el OAuth completo (re-Allow en Meta) en vez de solo reintentar el select (el `tempToken` podría seguir vivo). Decisión consciente = lado SEGURO (un fallo no deja credenciales vivas). Revisar con datos del E2E (paso 5): si los transitorios son frecuentes, diferenciar transitorio (no limpia) de 422-real (limpia). NO cambiar ahora.

**REGLAS DEL ARCO:** contrato capturado ✓ (ya no a ciegas) · un commit por paso + review del owner ANTES · no `persona_*`/`limits` · **cero publish hasta página verde en SU profile correcto verificada por el owner**.

---

## 🔴 HANDOFF · B-2 ZERNIO · cierre sesión 17 jun (fase de DIAGNÓSTICO · superada por el headless de arriba)

**COMMITS (gate 15/15 c/u · TODOS en origin · `main` sync · HEAD `b7b47af`):**
- `6ff8d0f` commit 1 · migr **00068** `zernio_profile_id` + adapter profiles/connect · **ORIGIN + PROD (00068 aplicada)**
- `6795856` commit 2 · endpoints profile/connect/connected + **zernio-sync HARDENED** · **ORIGIN + PROD**
- `2f74a8f` commit 3 · tab Cuentas OAuth-por-red white-label · **ORIGIN + VERCEL**
- `b7b47af` fix **botón honesto** (`connectButtonState` · no afirma sin confirmar Zernio) · **ORIGIN + VERCEL**

**PRUEBAS VIVAS (owner):** Omega Raisen (A) 4 cuentas → **verde ✓** · botón honesto OK (ámbar durante OAuth, no afirma antes de confirmar) · `DEBT-ZERNIO-MULTI-SAME-PLATFORM` registrada (upsert client_id+platform limit 1).

**🔴 BUG ABIERTO · PRIORIDAD MÁXIMA · `DEBT-ZERNIO-MAILBOXES-NO-ATTACH`:**
Síntoma: Mail Boxes (negocio B · `7663aa55`) conectó `mail_bd` IG → login completó → **NUNCA verde**.

**DIAGNÓSTICO CERRADO · RE-VERIFICADO EN VIVO 17 jun (datos frescos · idénticos al previo · CORRIGE la hipótesis del owner):**
La hipótesis "todas caen en un profile global" es **FALSA** — los profiles SÍ son per-negocio:
- **DB `clients.zernio_profile_id`:** Mail Boxes=`6a3302c498` · Omega Raisen=`6a32fe37aa` · Zafacones=`6a32f5ae05` (**3 ids únicos · DISTINTOS ✓**) · Milagrosa=NULL · Mi negocio=NULL.
- **Zernio `GET /profiles` (5):** Default · Raisen(viejo) · Zafacones Ramos · Omega Raisen · **Mail Boxes Design** → el profile de Mail Boxes **SÍ EXISTE** (`6a3302c498`, coincide con la DB).
- **Zernio `GET /accounts` (4):** las 4 son de Omega Raisen (raisenagency/omegaraisen) TODAS bajo su profile (correcto). **`mail_bd` NO existe en Zernio en NINGÚN profile.**

**RAÍZ REAL:** ensure-profile + connect-url FUNCIONAN (cada negocio tiene su profile propio · creado y guardado). El bug es que **la conexión de `mail_bd` NUNCA se adjuntó al profile de Mail Boxes en Zernio** (ausente de `/accounts`). Por eso `zernio-sync(7663aa55)` → `list_accounts(6a3302c498)`=vacío → **422** → no verde. **El hardening del commit 2 FUNCIONÓ** (se negó a marcar verde una cuenta ausente del profile · previno un cross-publish · es la defensa actuando, NO un fallo).

**RAÍZ — REFINADA POR TEST EN VIVO 17 jun (el probe corrigió mi hipótesis previa · profile de prueba creado+borrado sin residuo · profiles=5):**
El authUrl de `GET /connect/instagram?profileId=X` apunta **DIRECTO a `instagram.com/oauth/authorize`** (NO a una UI hosteada de zernio.com), con `redirect_uri=https://zernio.com/api/v1/connect/instagram/callback` (callback **server-side** de Zernio) y un `state` con esta estructura:
`{ownerId}-{profileId}-{timestampMs}-{finalRedirectUrl doble-encodeado}`.
→ **El `profileId` VIAJA EN EL `state`** (no depende de la sesión del navegador para saber a qué profile adjuntar) · el `finalRedirectUrl` por default = **`https://zernio.com/dashboard`** (= el `/dashboard` que vio el owner). Por lo tanto la hipótesis "el binding del profile depende de la sesión" es **demasiado fuerte**: el profile va en el state y el code-exchange es server-side. Lo que SÍ queda detrás del login de zernio.com es **el aterrizaje final (dashboard) y — para IG Business — el paso de SELECCIÓN de página/cuenta** (Zernio expone `list/select-facebook-page`, `step=select_page`). Hipótesis viva más precisa: el OAuth de `mail_bd` no se finalizó porque tras el "Allow" el aterrizaje cayó en `zernio.com/signin` (sin sesión) y **el paso de selección de cuenta IG-business nunca se completó** → la cuenta nunca quedó adjunta → ausente de `/accounts` → 422.

**CONTRATO HEADLESS — CONFIRMADO EN VIVO 17 jun (OAuth real · cuenta descartable `wudi.app` IG · profile de prueba · todo borrado tras capturar · profiles=5):**
El retorno headless (`headless=true&redirectUrl=<captura OMEGA>`) trajo, en el redirect, estos campos:
- **host destino = `omega-production-3c67.up.railway.app`** → **ATERRIZA EN NUESTRO DOMINIO**, NO en `zernio.com/signin`. ⇒ resuelve el aislamiento Y el white-label-redirect **de un golpe** (misma raíz, como se anticipó).
- **`profileId`** = el del profile de prueba → **viaja correcto** (la cuenta cae en el profile pasado).
- **`accountId`** = **VIENE DIRECTO EN EL RETORNO** (no hay que re-listar `/accounts` a ciegas · mejora vs la suposición previa de la doc).
- **`username`** = `wudi.app` (handle autoritativo de Zernio).
- **`connect_token`** = presente en el retorno.
- **`step=select_page` NO apareció para Instagram** (IG trajo `accountId` directo). **⚠️ OJO FB: para Facebook PODRÍA aparecer el paso de selección de página** (`list/select-facebook-page`) — **NO asumir que IG y FB se comportan igual al diseñar el fix.**
- (referencia) `redirectUrl` se honra; `pending-oauth-data` = `GET /connect/pending-oauth-data?profileId=…&platform=…`; `POST /accounts/{id}/move` existe (no aplicó); `DELETE /profiles/{id}` OK.
**CONTRATO CERRADO.** Próximo paso = planear (en commit aparte, con review del owner ANTES de tocar producción) la migración del connect-url de producción hosted→headless usando este contrato.

**EXPERIMENTO DE CAPTURA · `DEBT-ZERNIO-CAPTURE-ENDPOINT-TEMP` — ✅ CERRADA 17 jun (endpoint removido + profile/cuenta de prueba borrados profiles=5 + owner retira `ZERNIO_CAPTURE_TOKEN` de Railway):**
Para confirmar el contrato headless sin construir a ciegas se montó un endpoint TEMPORAL de captura:
`GET /api/v1/zernio-experiment/capture?cap=<token>` (`backend/app/api/routes/_zernio_experiment.py` +
1 línea en `main.py` + test 4/4). SIN JWT (recibe el redirect del navegador) → protegido por **token de
UN SOLO USO** (`ZERNIO_CAPTURE_TOKEN` env · 403 sin él · 410 al reusar · inerte si la env falta). **NO
persiste nada en DB**; `code`/`tempToken` JAMÁS completos en logs (solo presencia/len) · valor completo
solo en el HTML efímero. Disparo + limpieza por scripts locales en `%TEMP%` (`zernio_exp_start.py` /
`zernio_exp_cleanup.py` · profile de PRUEBA `OMEGA_EXP_*` descartable). **CERRAR ESTA DEUDA = borrar el
archivo + la línea de `main.py` + retirar la env var de Railway + correr cleanup**, una vez capturado el
contrato. Plan completo en `~/.claude/plans/jiggly-fluttering-simon.md`.

**WHITE-LABEL (pendiente · menor que el bug · misma raíz probable):**
1. popup salta a `zernio.com/signin`+`/dashboard` tras Allow → ¿`getConnectUrl` admite `returnUrl/redirectUrl/callback`? (docs.zernio.com).
2. "Social Media Connector" en consent Meta/TikTok = nombre de la app de Zernio → confirmar si Zernio permite white-label del nombre o exige app propia (= App Review/audits, lo que B-2 evita).
3. el `zernio.com/signin` que vio el owner: ¿artefacto de SU sesión de prueba (logueado) o lo vería un cliente externo? Clave — si es lo primero, en prod (API key server-side) medio problema desaparece.

**REGLAS PERMANENTES:** NO tocar `persona_nova.py`/`persona_aria.py`/`limits_omega.py` · NO tocar el profile viejo "Raisen" ni las 4 cuentas de prueba de Omega Raisen · identidad git raisenomega · gate 15/15 + test-first (G3) · **UN commit por parche · PARAR para review del owner ANTES de cada avance · ninguna instancia se auto-aprueba** (pasó un auto-accept ⏵⏵ antes · vigilar) · **CERO publish en vivo** hasta que un negocio B tenga una cuenta **verde en SU profile correcto**, verificado por el owner. Scripts diag read-only en `C:\...\Temp\zernio_*.py` (no-repo).

---

## REGLA GLOBAL ÚNICA · JAMÁS TOCAR NOVA NI ARIA
Establecida por el owner (Ibrain) · Sesión 4 (4 jun 2026) · Grabada formalmente · Sesión 5 (5 jun 2026)

ARCHIVOS PROTEGIDOS (INTOCABLES):
- backend/app/bc_cognition/domain/persona_nova.py   (SHA1 bef773c9)
- backend/app/bc_cognition/domain/persona_aria.py   (SHA1 054a17f3)

REGLA: El system prompt de NOVA y el de ARIA NO se modifican. NOVA es la máxima eminencia (solo
habla con Ibrain). ARIA es la única cara hacia cliente/reseller. Son infraestructura, no componentes.

Cualquier modificación de estos dos archivos requiere, sin excepción:
1. Autorización del owner EXPLÍCITA y LITERAL, caso por caso. Ninguna instancia (Claude.ai ni
   Claude Code) escribe "autorizo" en nombre del owner.
2. Ritual X2 completo (test TDD que falla primero + rotación de SHA1 + commit del nuevo baseline
   en scripts/personas-sha1.txt).
3. Justificación documentada.

NUNCA se modifican: por presión del reseller · por urgencia de un cliente · por "esta vez es
diferente" · ni dentro de un refactor más grande.

JERARQUÍA: IBRAIN → NOVA (cerebro, solo Ibrain) → ARIA (única cara) → agent_memory + was_correct
→ NOVA crece → orquesta 8 agentes operativos + SOPHIA + GUARDIAN.

NOTA: El runtime DEBE LEER estas personas como fuente única (fix Sesión 5: NOVA runtime lee
persona_nova vía _context_builder). Leerlas NO es modificarlas. Lo prohibido es alterar su contenido.

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
> ⚠️ **SUPERSEDED (24 jun 2026 · arco cuentas-dueño · ver `SOURCE_OF_TRUTH.md §6` cierre 24 jun).** El bypass por **emails hardcodeados** y el `useDemoMode` (toggle VISTA) **ya NO existen** (A2.2 `bb19bd3` los borró). La exención de PAGO vive ahora en la tabla **`owner_accounts`** (migr 00074 · DDD · NO hardcode) y cubre SOLO `reseller@omega.com` (`61f88b91`) + `raisen@omega.com` (`84d86286`). **`cliente@omega.com` NO está en `owner_accounts`** — sigue Enterprise por su fila de DB, no por la exención. Eximen de PAGO, NUNCA de aislamiento (`is_owner=false`). Lo de abajo queda como registro histórico.
- **`cliente@omega.com`** · client `Zafacones Ramos` (`afb9f578-...`) · DB: `clients.plan='enterprise'` + `client_plans.plan='enterprise'` + addons `[video_pack_cinematic_pro, brand_dna_premium, aria_pro]` + `current_period_end=2099-12-31` + `client_agent_credits.budget=$99,999.99/mes` periodo `2099-12-31`. ~~FE: `useDemoMode` default `'enterprise'`; toggle Enterprise/PRO/Básico~~ (selector demo eliminado en A2.2).
- **`reseller@omega.com`** · `resellers.plan='enterprise'` (era 'pro')
- **Owner Ibrain** (`OMEGA Direct` · user `741ace1c-...`) · `plan='enterprise'` + `is_super_owner=True` desde antes — no necesita demo mode.
- **Política (actualizada)**: la exención de pago se otorga agregando el `user_id` a `owner_accounts` (NO hardcode de emails, NO bypass nuevo por gate). Si aparece un gate de pago, exime vía `owner_accounts`, nunca por email hardcodeado.

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
**Heredados pre-Sprint1:** DEBT-002 (Math.random analytics 🟡) · DEBT-004 (202 archivos >75L 🟢) · DEBT-008 (frontend→Supabase directo 🟡) · DEBT-OWNERSHIP-TRIAGE 🟢 · DEBT-ORPHANED-TABLES 🟢 · DEBT-ANTIFRAUD-WIRE 🟡 · DEBT-ENTERPRISE-PRICE-GUARD 🟢 · **DEBT-SCHEMA-DRIFT-RESELLER 🟡 (NEUTRALIZADO 19 jun · reclasif. desde 🔴 BLOCKER — NO bloquea launch ni REX · ver Diagnóstico 2)** · DEBT-DRAFTEDIT-TZ 🟡 (20 jun · `DraftEditForm.tsx:70` manda `scheduled_for` sin `toUtcIso` → un post agendado por ESE path se guarda naive y REX lo dispararía a hora equivocada · el path principal `useScheduleBlock.ts:36` SÍ convierte a UTC, OK · NO bloquea REX F1 · fix = aplicar `toUtcIso` también en DraftEditForm) · DEBT-REX-CRISIS-AUTO 🟡 (20 jun · `clients.crisis_active` es kill-switch MANUAL en REX F1; cablear que `crisis_manager`/`crisis_detector` lo enciendan solo al detectar crisis — hoy detección es on-demand sin persistencia · follow-up post primer incremento REX) · DEBT-WORKER-LOGS-TABLE-MISSING 🟡 (20 jun · `omega_worker_logs` NO existe en prod · `BaseWorker._log` falla best-effort → workers loguean a stdout/Railway en vez de DB · PREEXISTENTE · afecta a TODOS los workers, no solo REX · no rompe nada · crear la tabla o quitar el log a DB) · DEBT-ARIA-LEVEL-TRUST 🟢 (20 jun · checklist PRE-PRODUCCIÓN · NO arreglar ahora): el nivel efectivo de ARIA se lee de `clients.aria_level` a ciegas (`message.py:31`) sin re-derivar de plan+addons. HOY sin riesgo: los únicos "adelantados sin addon" son las cuentas de dogfooding del owner (reseller@omega.com/cliente@omega.com/raisenagencypr · forzadas a propósito para probar E2E) · ningún cliente real desalineado (scan 20 jun). ANTES de lanzar (post-90d): reconciliar `aria_level`↔plan+addons para que (a) nadie obtenga premium sin comprarlo (b) un enterprise no quede sub-servido (Zafacones enterprise tiene aria=1 · recibe < lo que su plan otorga · cara opuesta). Hardening pre-launch, no bug activo · cuentas del owner quedan adelantadas a propósito durante el dogfooding. · DEBT-ROTAR-KEYS-PRELAUNCH 🟠 · DEBT-106A/B/C/D (Claude DEV ~40h 🟢) · DEBT-2FA-SUPERADMIN (4h 🟠 sugerido).

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

> **Input Sanitizer · cierre gaps (Sesión 3 · 3 jun · spec firmada PROTOCOLO_SEGURIDAD_INPUT_OMEGA):** hallazgo = el sanitizer YA estaba ~85% implementado (Sprint 4A) y **spec-compliant** (`domain/input_threats.py` + `application/input_sanitizer.py` · T1-T7 · caps §8.6 · fail-closed §8.5 · 9 tests). Auditoría action-handling de los **6 callers existentes = TODOS compliant** (ARIA_CHAT/CONTENT_PROMPT/RESEARCH×3/UPLOADED_DOCUMENT + agent_memory PII §8.2 vía `redact_pii`). **Cerrados los 3 gaps de integración** (consumidores §6 faltantes): `generate_image` + `generate_video` (sanitize prompt · CONTENT_PROMPT · BLOCK/HOLD→400) + `brand_voice_corpus` ×2 sites (manual_upload en `_clients_repository` + approved_draft en `content_v3/_content_repository` · BRAND_CORPUS · skip-on-unsafe + clean_text · contexto antes definido-pero-nunca-usado). +3 tests (12 total). **Cobertura: 6/6 consumidores §6 cubiertos.** Per spec firmada: SIN tabla sanitizer_holds + SIN card UI (no están en §1-§9 · V1 backend-only). **2 DEBTs nuevas:** `DEBT-SANITIZER-HOLD-PERSISTENCE` (🟢 ~2h · tabla `sanitizer_holds` + endpoint approve/reject · ampliación post-data-real) · `DEBT-SANITIZER-CARD-UI` (🟢 ~3h · card panel + stats threats · V2 con tráfico). Próxima sesión: GUARDIAN Subsistema (spec firmada 24 may · 4B-1 a 4B-5 · ~15-20h).

> **GUARDIAN 4B-1 expandido (Sesión 3 · 3 jun · spec GUARDIAN_SECURITY_AGENT):** hallazgo = GUARDIAN ya ~90% construido (Sprint 4B · migr **00022** 3 tablas+RLS+is_owner=1 · `guardian_session_analyzer`/`guardian_threats` · `login_event`/`session_report` · `GuardianTab.tsx` básico funcional). **No recree nada.** Migración **00065** = ALTER (no duplica): +`session_id` +`device_fingerprint` (user_security_log) +`resolution_notes` (security_incidents) + indexes. **Geo ACTIVO** (owner pidió ahora · `geo_lookup_adapter.py` httpx directo a IPinfo · sin SDK · token-opcional · **smoke 8.8.8.8→US/California/Mountain View** · IP privada→None fail-open · skip privadas/loopback) cableado en `analyze_login`→`insert_security_log` (country+geo) + `session_report` muestra country. **5 acciones owner end-to-end** (4 endpoints `/guardian/actions/*` · gated `require_superadmin`): block-ip (ip_watchlist+resolve incidente) · force-logout (GoTrue admin REST `/logout` + fallback ban 24h) · resolve-incident (resolved/false_positive en 1 endpoint con flag · DRY) · trigger-password-reset (`reset_password_for_email`). Gate 11/11 (cacé config.py 101→100L · crónico). **DEBTs cerradas:** GUARDIAN-GEO-INTEGRATION (geo activo) · IPINFO-TOKEN (owner agrega). **DEBTs nuevas:** `DEBT-GUARDIAN-DEVICE-FINGERPRINTING` (🟢 ~4h) · `DEBT-GUARDIAN-LEARNING-LOOP` (🟢 ~4h · false_positive realimenta el analyzer) · `DEBT-GUARDIAN-PASSWORD-RESET-CUSTOM-TEMPLATE` (🟢 ~1h) · `DEBT-GUARDIAN-FORCE-LOGOUT-FALLBACK` (🟢 · si GoTrue REST /logout no responde, usa ban — ya implementado como fallback). **PRÓXIMO TURNO 4B-4/4B-5:** UI GuardianTab SENTINEL-style (Estado por componente + chips clickables + modal universal con las 5 acciones cableadas + ver IP/país/hora/email/session/UA/device). Backend de acciones LISTO; falta cablear UI + testear acciones con JWT owner en vivo.

═══════════════════════════════════════════════════════════════
## 🛡️ CIERRE SESIÓN 3 · TOTAL (3 jun 2026) · Input Sanitizer + GUARDIAN end-to-end

**Commits clave:** `4b9aa9d` Input Sanitizer gaps · `b2389ad` GUARDIAN 4B-1 (geo+acciones backend) · `602d593` UI 4B-4 base · `7461999` modal acciones · `1437dff` smoke real · `8d9fe79` pulido · `c4d9180` Claude Consultor.

**Input Sanitizer:** spec PROTOCOLO firmada · **6/6 consumidores** (ARIA/content/image/video/research/upload/brand_corpus + agent_memory PII §8.2). Cerrado.

**GUARDIAN end-to-end (camino C · specs firmadas primero):**
- Backend (00022 + **00065** ALTER session_id/device_fingerprint/resolution_notes): 3 tablas+RLS+is_owner · analyzer heurística · login/session.
- **Geo ACTIVO** (IPinfo · `geo_lookup_adapter` httpx · fail-open · smoke 8.8.8.8=US/California) — extensión owner (§7.6 era fase-posterior).
- **UI estilo SENTINEL** (`/security-dev`→GUARDIAN): header+3 KPIs · 3 cards expandibles (chips filtran) · `GuardianDetailModal` (detalle real: email/IP/país/session/UA/historial/incidents/watchlist) — supersede las 2 cards básicas §8 (extensión owner).
- **5 acciones owner e2e** (`/guardian/actions/*` · require_superadmin · **smoke real 200**: block-ip, resolve, false-positive, password-reset [email enviado]; force-logout omitido [protege sesión] · verificado code-path).
- **Claude Consultor** (extensión owner · §7.2 era fase-posterior): `guardian_consultor`→Sonnet 4.6 · `/guardian/consult/incident` · contexto ≤2k · agent_memory audit · smoke local OK (recommended_action + confianza + cita evidencia · P1).

**Compliance:** GUARDIAN_SECURITY_AGENT v1 cubierta + 3 extensiones owner-aprobadas (geo/Consultor/panel) · PROTOCOLO compliant · **cero gaps**.

**DEBTs nuevas (Sub-E):** `DEBT-GUARDIAN-CONSULTOR-FULL-CHAT` (🟢 ~3h · multi-turno vía Claude Dev page) · `DEBT-GUARDIAN-CONSULTOR-LEARNING` (🟢 ~3h · was_correct realimenta prompts) · `DEBT-GUARDIAN-CONSULTOR-EXECUTE-SHORTCUT` (🟢 ~1h · botón "ejecutar acción recomendada"). Previas 4B-1 siguen: DEVICE-FINGERPRINTING · LEARNING-LOOP · PASSWORD-RESET-CUSTOM-TEMPLATE · FORCE-LOGOUT-FALLBACK.

**Pendiente owner:** validación visual del tab GUARDIAN tras deploy Vercel · agregar `IPINFO_TOKEN` a Railway (geo funciona tokenless mientras tanto). **Próxima Sesión 4 = decisión owner:** 4A cerrar DEBTs heredados (024/025/provision) · 4B GUARDIAN enterprise (behavior profiling/threat-score/forensic · con tráfico real) · 4C Tier-1 a 10/10 (AWS+GCP failover + pentest).

> **Sesión 6 jun (FASE 2 NOVA · Pieza 1 + Pieza 2 sub-paso 2.0 + diagnóstico flujo ARIA→NOVA):** **Pieza 1 CERRADA** (GAP-3 `9d52607` client_context no-destructivo · GAP-1 `4799251` las 4 CHAINS del orchestrator despachan a codes canónicos reales) + **sub-paso 2.0 CERRADO** (`93e8ad0` · `client_id` explícito del Switcher en chat de NOVA · prioridad sobre nombre · validación de existencia owner-only · molde de ARIA · gate 10/10 · smoke a/c/anti-clobber verdes). **Diagnóstico read-only flujo canónico ARIA→agent_memory→NOVA:** eslabón 1 ✅ (`use_aria_message`+`aria_memory_repository` insertan `agent_code="aria"` `memory_type="episodic"` was_correct None/False) · eslabón 2 ✅ activo (cron `decision_evaluator` `main.py:174` minute=30 · agnóstico de agent_code · **DB prod: 116 filas aria · 91 con `evaluated_at` puesto → corre en vivo** · was_correct True=0/False=2/null=114) · **eslabón 3 ❌ CORTADO al diagnóstico — CERRADO después (ver cierre 6 jun abajo)** (NOVA solo lee `agent_code="NOVA"` en `chat.py:71`+`get_briefing.py:44` y memoria de agentes @mencionados en `_memory_handler`; **cero lectura de `agent_code="aria"` en toda la superficie de NOVA** · grep definitivo vacío · `oracle_service` escribe ORACLE/no lee aria · el brief no agrega learning/accuracy de ARIA). **2 DEBTs nuevas registradas (sin fix):** `DEBT-CONTEXT-LIBRARY-MISSING` 🟠 — `get_client_context` (`_context_builder.py`) consulta la tabla `context_library` que **NO EXISTE en prod** (PGRST205) → el fallback por nombre del chat de NOVA siempre devuelve vacío (afecta @mención + banner "Cliente activo" del NOVA path) · sub-paso 2.0 lo elude usando `client_id` explícito · `DEBT-CLIENTS-DUP-ZAFACONES` 🟠 — **2 filas "Zafacones Ramos" en `clients` ambas status=active** (`afb9f578` curado el que lee ARIA/`client_context` · `7d9d4335` el otro) · `ilike "%name%" limit 1` resuelve al equivocado (`7d9d4335`) → confirma por qué la resolución por nombre es **activamente incorrecta** (refuerza el valor del `client_id` explícito de 2.0). **Implicación eslabón 3 (decisión owner):** NOVA no aprende de lo que ARIA captura — candidato a Pieza 3 (bridge ARIA→NOVA: brief/contexto de NOVA agrega decisiones+accuracy de `agent_code="aria"`).

> **Sesión 6 jun PM · CIERRE (Eslabón 3 + Autoconciencia + Loop de verdad) · personas intactas `bef773c9`/`054a17f3` todo el camino.**
> **ESLABÓN 3 ARIA→NOVA · CERRADO en prod (4 commits).** NOVA ahora consume el stream de ARIA: fachada `nova_aria_learning.py` (`1b66ef7` · conteos honestos `with_real_verdict` excluye fallos API · cero accuracy %) → briefing sección 8 "Aprendizaje de ARIA" (`d929ea5` · global) → chat per-negocio en `build_nova_system_prompt` (`bbf791e`) → **fix shadowing `client_id`** (`d29ec40` · la tupla de `get_client_context` pisaba el param → el bloque ARIA nunca se inyectaba · destapado por el smoke per-4-negocios, no el de 1). Verificado en vivo con los 4 negocios: cada uno cita SUS interacciones reales, anti-cross-tenant AISLADO, conteos honestos. Supersede el "❌ CORTADO" del diagnóstico de arriba.
> **PUNTO 6 · AUTOCONCIENCIA DE NOVA · CERRADO en prod (`921c3ca`).** Módulo `_capabilities.py` (`build_capabilities_block` · git_sha env + CHAINS + roster canónico + SENTINEL score + veredictos reales · cacheado 10min · fail-safe POR query) inyectado en el system del chat (alta prioridad en `reserved`, persona prefijo intacta). Regla P1 `_REGLA_P1`: prohíbe inventar grado de completitud global (%/fracción/etiqueta). Smoke post-push: NOVA cita inventario real + NO-HECHO honesto y **rechaza activamente inventar completitud** ("sería sintético · violaría P1") · el desglose 75/60/40/5/30 del 1er smoke desapareció. **`DEBT-NOVA-SELF-AWARENESS` CERRADA** por este wiring.
> **PUNTO 0 · LOOP DE VERDAD · DEPLOYADO forward-only (3 commits `8bd5115`→`e7842e7`→`0f9b33b` · gate 10/10 · 249 tests).** Causa raíz: `agent_memory.source_event_id` de aria apuntaba a `behavioral_events` (aria_message_sent), pero `evaluate_decisions` lo buscaba en `content_lab_generated` → **0/116 cierres**. Fix Opción A-precise: capturar el `content_id` del draft EN la generación (`run_tool_loop` lo devuelve → `use_aria_message` lo threadea a ambos paths → `insert_agent_memory` lo guarda en `aria_nba_id`, columna muerta reusada SIN migración) y `_decide` cambia la KEY del join a `aria_nba_id` (`source_event_id` SE CONSERVA, solo deja de ser key). Smoke lean local PASS (puente real encadenado + cleanup verificado ante fallo real). Post-push: turno ARIA real 200 normal (la tupla de 3 no rompió `use_aria_message` en vivo · fila Q&A `aria_nba_id=None` honesto) · DB directo **0 filas `aria_nba_id` poblado**. **`DEBT-ARIA-VERDICT-LINK` 🟢 RESUELTA EN MECANISMO · forward-only · el PRIMER VEREDICTO REAL está pendiente de tráfico post-deploy** (un cliente que genere+apruebe un draft y el cron lo cierre · horas/días). NO marcar "cerrada con datos reales" hasta ver `agent_memory where aria_nba_id not null and was_correct=True` > 0 en DB (hoy = 0, esperado).
> **DEUDAS:** `DEBT-ARIA-DIRECT-SIGNAL` 🟡 (Opción B · señal directa de aceptación en la conversación · requiere capturar un evento de aceptación que HOY no existe y roza P1 — NO se hace ahora por diseño, no por olvido) · `DEBT-CLIENTS-DUP-ZAFACONES` 🟠 + `DEBT-CONTEXT-LIBRARY-MISSING` 🟠 (siguen abiertas · ver diagnóstico arriba) · **GAP-2** (NOVA orquesta chains desde el chat) sigue deuda futura mayor, sin cambios · GAP-1 alineación de chains + 2.1 detección de intención ya cubiertos/pendientes según Pieza 1/2.
> **LECCIÓN C4:** `app/bc_cognition/` NO está exento del límite 100L (la exención es solo `app/api/*` + `app/infrastructure/*`, NO `app/bc_cognition/infrastructure/*`). Verificar LOC de TODOS los archivos tocados antes del push (el gate bloqueó el 1er push de Punto 0 por 3 archivos >100 · fix = compactar docstrings + split de test, cero lógica, commits reconstruidos limpios).
═══════════════════════════════════════════════════════════════

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
1. ✅ **IDOR / cross-tenant (8 jun · remediado):** el audit confirmó `analytics/dashboard` como FALSO POSITIVO (el router gatea). Los endpoints legacy sin ownership (scheduling, clients/ legacy, brand_files) → ELIMINADOS/parcheados (INCIDENTE-SEC-002 · 16 endpoints · 3 fases · pointer SOURCE §6 · detalle `*.local.md`). Pendientes menores con triggers (reseller DELETE, context latente, feature_usage).
2. ✅ **NEUTRALIZADO (19 jun):** Endpoints reseller billing/stats/detail/dashboard/oracle/public ya NO 500-ean contra columnas inexistentes (`omega_commission_rate`, `monthly_revenue_reported`, `agency_name`) — selects alineados a columnas reales + `.get()` fallback honesto. **Bonus:** login de reseller arreglado (lookup fantasma `resellers.owner_email` eliminado · usaba `clients.reseller_id`). Schema reseller real se diseña en Sprint 8.
3. ✅ **NEUTRALIZADO (19 jun):** Crear reseller ya no intenta el INSERT roto (a `resellers` con columnas fantasma ni a `clients`) → degrada honesto con **501 `reseller_provisioning_pending_sprint8`**. Provisioning completo (incl. `owner_user_id`/auth) = Sprint 8 con Modelo C firmado.
4. ✅ **SENTINEL NO ciego** (verificado 20 jun · `sentinel_scans` 00048 real · el cron escribe ambas tablas · 33/19 filas en prod · falso positivo del audit) · **anti-fraude no cableado** (tabla sin código · DEBT-ANTIFRAUD-WIRE).
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
1. 🟡 **IDOR legacy (8 jun · mayormente remediado):** endpoints legacy sin ownership cerrados en 3 fases (INCIDENTE-SEC-002 · pointer SOURCE §6 · detalle `*.local.md`). `analytics` = falso positivo (gateado). Pendientes: reseller DELETE, context (latente), feature_usage.
2. 🟠 Sin defensa-en-profundidad (service_role bypassa RLS; aislamiento depende del guard por handler; analytics lo olvidó).
3. 🟠 Controles doc no implementados: rate-limit, account-lockout, token-revocation, failover LLM, GitHub Actions (`.github/` no existe), SHA1 worker.
4. 🟠 Anti-fraude NO cableado (tabla 00004 sin código) — superficie del trial $0/7d.
5. ✅ SENTINEL NO ciego (verificado 20 jun · ambas tablas reales+pobladas · falso positivo).
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
| 6 | ✅ | SENTINEL NO requiere arreglo (verificado 20 jun · ambas tablas reales · el cron escribe ambas · falso positivo). |
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
- ~~**SENTINEL fantasma**~~ → **FALSO POSITIVO (20 jun):** `sentinel_scans` (00048) es real y poblada (33 filas) · el cron `run_full_scan` escribe ambas tablas · cero cambio de código.
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
🟡 **`resellers` — 10 columnas fantasma (NO 6) que el código referencia pero NO existen en prod ni en migraciones** (verificado 19 jun contra código real · `tier` se descartó: era de `bc_billing`/packs, no de resellers): `agency_name`, `owner_email`, `owner_name`, `omega_commission_rate`, `monthly_revenue_reported`, `payment_due_date`, `days_overdue`, `suspend_switch`, `clients_migrated`, `white_label_active`. El schema canónico real = 15 cols (11 base + `is_owner`/`aria_level`/`addons`/`is_super_owner`). **NO bloquea REX** (se para sobre `clients`, sano). **Diferido a Sprint 8** (schema definitivo = Modelo C · `omega_commission_rate` se elimina ahí).

**✅ NEUTRALIZADO (19 jun · red de seguridad · sin tocar prod · 7 puntos · gate 15/15 · 5 tests no-500):**
- `get_reseller_stats.py:19` / `get_reseller_billing.py:20` — `.select()` solo columnas reales + `.get()` fallback (commission_rate→30, mrr→0).
- `oracle_service.py:38` — `.select("id, status")` (quitado `agency_name`, no se usaba).
- `public.py:123` — `agency_name` → `reseller.get("agency_name") or reseller.get("name")` (no KeyError).
- `admin.py` create_reseller → **501** `reseller_provisioning_pending_sprint8` (en vez de INSERT roto a `resellers`+`clients`). Cubre también el drift de `clients` (`password_hash/role/...`): ese INSERT ya no se intenta.
- `admin.py` update_reseller_status — descarta `suspend_switch` (fantasma) + guard si no hay cambios reales (status sí es columna real).
- `login.py:107` — eliminado el lookup `resellers.owner_email` (columna fantasma que 500-eaba el login del reseller) → usa `clients.reseller_id`. **Bonus: arregla login de resellers.**
- Test `resellers/tests/test_schema_drift_safety.py` (5 casos · simulan schema real · prueban degradación honesta).

**✅ `clients` CONFIRMADO sano para REX (19 jun · verificado en migraciones + código vivo):** `reseller_id`/`industry`/`plan` (00001) · `region`/`aria_level`/`industry` (00008 `aria_intelligence_schema` · ALTER multilínea) · `zernio_profile_id` (00068) — todas presentes y `clients_v3/handlers/get_client_profile.py:22` las SELECTea en prod. **REX puede arrancar sobre `clients`; NO depende del drift de `resellers`.** El drift de `resellers` queda diferido a Sprint 8 sin bloquear el camino.

✅ **`sentinel_scans` — VERIFICADO REAL (20 jun · la hipótesis "tabla fantasma → ciego" era FALSA en los dos puntos):** las DOS tablas existen — `sentinel_scans` (migr **00048**) y `sentinel_risk_scores` (migr **00029**). El cron `run_full_scan` (7am AST · `main.py:114`) escribe **AMBAS** (`sentinel_service.py:63` = 3 filas/corrida VAULT/PULSE/DB_GUARDIAN · `:71` = 1 agregada) y todo lector lee una tabla poblada (oracle/nova/panel SENTINEL → `sentinel_scans` · panel security-dev/`get_summary` → `sentinel_risk_scores`). **Conteo prod read-only:** `sentinel_scans`=33 · `sentinel_risk_scores`=19 · última fila IDÉNTICA `2026-06-19 11:00:01 UTC` (misma corrida del cron). **SENTINEL NO está ciego · CERO arreglo de código.** Consistente con DEBT-SENTINEL-BLIND ya CERRADA (3-jun · 00048). El 🔴 previo era falso positivo del audit del 10-jun (no podía ver el schema real).

**Tablas sin uso de código — CORREGIDO 20 jun (verificado contra código real · el registro previo se equivocó):**
- ❌ `training_pairs` **NO está huérfana** — `bc_cognition/application/aria_learning_report.py:53` la LEE (reporte semanal ARIA learning · ventana 7d). Sacada de la lista de huérfanas. (Aparte: quién la POPULA sigue abierto, pero la tabla está cableada en lectura.)
- 🟢 `aria_nba_log` + `cross_client_benchmarks` (migr 00008): **0 uso en código HOY, pero NO son deuda a limpiar** — son la infraestructura de aprendizaje (Loop 2 · `was_correct` · cross-client benchmarks) que **REX/Centro van a cablear**. Activo listo para usar, NO borrar. La forma de que dejen de estar "vacías" es construir REX, no borrarlas.
- 🟡 `anti_fraud_signals` (migr 00004): sin cablear (ver DEBT-ANTIFRAUD-WIRE).

✅ **`learning_events` — nunca se creó** (sospecha confirmada por la auditoría).

### Decisión de producto reseller — RESUELTA (Opción C · 19-20 jun)
El camino reseller (#3/#4) se cerró con **Opción C** (ni A ni B puros): neutralización honesta (7 puntos · 0 500s · login reseller arreglado de paso) + schema definitivo **diferido a Sprint 8 con Modelo C** — no se cementó prod a código especulativo. Detalle en `DEBT-SCHEMA-DRIFT-RESELLER`. (SENTINEL nunca fue parte real: falso positivo · ver arriba.)

---

## DEUDAS NUEVAS REGISTRADAS — 2026-06-02

✅ **DEBT-IDOR-NOVA** · ~~CERRADA 3-jun · `715aab3` backend (require_superadmin en los 11 endpoints) + página NOVA frontend `8262925` (super_owner-only) full-width + localStorage (últimos 50) + borde a borde (`6a0ce24`/`36afac6`)~~. (original) módulo `/nova` (11 endpoints) sin auth ni ownership. Lectura + escritura + ejecución de acciones del CEO Agent de cualquier cliente, sin login.

✅ **DEBT-IDOR-ANALYTICS** · ~~CERRADA 3-jun · `8b2da5e` (auth + ownership en los 7 endpoints + `GET /dashboard/` agg gated por require_superadmin)~~. (original) módulo `/analytics` (7 endpoints) sin auth. Lectura cross-tenant sin login; `GET /dashboard/` agrega TODOS los clientes si no pasás `client_id`.

🟠 **DEBT-OWNERSHIP-TRIAGE:** 11 módulos autenticados sin verificación explícita de ownership del `client_id`. Triage: separar legítimos (super-admin, reseller-scope) de IDOR-autenticado real. Lista en Diagnóstico 1. Trigger: después de los 2 críticos sin auth.

🟡 **DEBT-SCHEMA-DRIFT-RESELLER** (consolida la antigua `DEBT-RESELLER-PATH-DEAD` · era la MISMA deuda con dos nombres): el código reseller referenciaba 10 columnas fantasma en `resellers` (+ INSERT a `clients` con cols inexistentes) → billing/stats/detail/dashboard/login **500**. **NEUTRALIZADA vía Opción C (19-20 jun · `1ffa66c`):** 7 puntos degradan honesto (selects a cols reales + `.get()` fallback + create→501 + login reseller arreglado) · 0 500s · verificado en vivo (endpoint público reseller 200). **Schema definitivo diferido a Sprint 8 con Modelo C** (`omega_commission_rate` se elimina ahí · no se cementó prod a código especulativo). NO bloquea REX (se para sobre `clients` sano).

✅ **DEBT-SENTINEL-BLIND** · ~~CERRADA 3-jun · migración 00048 (sentinel_scans materializada) + db push aplicado + E2E verificado: schema 11 cols + RLS service_role + POST /sentinel/scan/ 200 + 3 filas reales (VAULT/PULSE_MONITOR/DB_GUARDIAN) + /sentinel/status·history·deploy-check pueblan correctamente~~ + commit `7627424`. (corrección a la hipótesis de auditoría: NO era rename a `sentinel_risk_scores` — son modelos distintos; se materializó `sentinel_scans` per-agente, cero cambio de código). (original) SENTINEL escribe/lee a `sentinel_scans` (no existe). Panel ciego (siempre "todo OK").

🟢 **DEBT-ORPHANED-TABLES (CORREGIDO 20 jun · verificado contra código):** `training_pairs` **sale** (la lee `aria_learning_report.py:53` · no es huérfana). `aria_nba_log` + `cross_client_benchmarks` (00008) = **cimientos de REX/Loop 2, NO deuda** (cero uso hoy · los cablea REX cuando se construya · documentados como activo listo, no a borrar). Solo `anti_fraud_signals` (00004) queda sin cablear → DEBT-ANTIFRAUD-WIRE. **Cero tablas a borrar.**

### DEUDAS NUEVAS REGISTRADAS — 2026-06-03 (cierre IDORs)

🟠 **DEBT-ANTIFRAUD-WIRE** (~8h · pre-launch externo): la tabla `anti_fraud_signals` existe en prod (00004) pero 0 código la usa (confirmado auditoría 2-jun). El trial $0/7d sin detección de abuso es superficie de fraude (multi-cuenta · device fingerprint · patrones anómalos). Cablear: detectar signals típicas, INSERT en `anti_fraud_signals`, gate de creación de nuevos clientes flagged → require_superadmin manual. Trigger: antes del primer onboarding externo real.

🟢 **DEBT-ENTERPRISE-PRICE-GUARD** (~1h · pre-launch externo): hoy checkout Enterprise usa `STRIPE_PRICE_ENTERPRISE` del env. Si vacío/ausente Stripe cobra lo que tenga el env o devuelve error opaco. Falta guard explícito en startup que falle si no hay price ID Enterprise. Patrón ya usado en otros price IDs del repo. 1 línea defensive.

🔴 **DEBT-SCHEMA-DRIFT-RESELLER** (~4h · BLOCKER decisión reseller CAMINO A vs B): Rec #1 BLOCKER del auditor 2-jun. La MCP Supabase apunta al proyecto equivocado · schema real de prod (`rwlnihoqhxwpbehibgxu`) no consultable. Las 6 cols faltantes en `resellers` + 5 en `clients` la auditoría las dedujo del código (SELECT/INSERT), no del schema real. Acción: `supabase link --project-ref rwlnihoqhxwpbehibgxu` · `supabase db dump --schema public` · diff vs migraciones canónicas. SIN este step la decisión CAMINO A (construir, semanas) vs CAMINO B (código honesto, días) se toma a ciegas. Precondición de DEBT-RESELLER-PATH-DEAD.

*Diagnósticos read-only · 2026-06-02 · embebidos en ESTADO_OMEGA · NO pusheados (owner decide).*

═══════════════════════════════════════════════════════════════
## 🔱 CIERRE SESIÓN 5 · 5 jun 2026 · FASE 1 IDENTIDAD ÚNICA DE NOVA (verificado en vivo · HEAD `4949b15`)

- **DEBT-ARIA-DEGRADED-IN-PROD: ✅ CERRADA · FALSA ALARMA.** Sesión 4 NO degradó ARIA (exonerada por código + data + 2 smokes en vivo). El síntoma era **artefacto de testing**: el owner probó ARIA logueado como él mismo (reseller, cartera N>1) **sin seleccionar negocio activo** en el Switcher → `client_id=null` → `resolve_role` legacy → respuesta genérica de reseller. **ARIA backend 100% sano**: clientes PYME reales (N=1 → auto-select) reconocen su negocio (SMOKE A en vivo lo confirmó con "Zafacones Ramos"). No hay bug de producción.
- **DEBT-NOVA-RUNTIME-DOES-NOT-REFLECT-PROMPT: ✅ CERRADA** (`058dfb9`). El runtime de NOVA leía un `NOVA_SYSTEM_PROMPT` legacy hardcoded en `_context_builder.py` ("7 directores / 45 agentes") en vez de `persona_nova.py`. Ahora importa la persona canónica (fuente única). Verificado en vivo: NOVA dice **"8 operativos + SOPHIA + GUARDIAN + ARIA cara"**, sin 45/37.
- **FASE 1 · IDENTIDAD ÚNICA DE NOVA: ✅ CERRADA y verificada en vivo.** 4 commits: `5c00d04` `canonical_agents.py` (fuente única 8 operativos + SOPHIA latente + GUARDIAN sub-sistema + 44 alias legacy→code) · `ade0174` `agent_registry` deriva del canónico (firma intacta, dispatcher sin tocar) · `30d39b5` chat.py @mención→code canónico + inactivos honestos · `b1f66e0` roster (context + briefing) desde CANONICAL_AGENTS. **+2 fixes de `temperature` deprecado** (`7350663` chat.py NOVA path · `4949b15` AnthropicProvider dispatch opus). **5 smokes verdes en vivo:** briefing=8 · NOVA lista 8+SOPHIA+GUARDIAN+ARIA · `@ATLAS`→strategy real (`fallback_used=False`) · `@VERA` inactivo honesto · `@SENTINEL` opus despacha 200. **pytest real 218/0.**
- **Personas intactas todo el tiempo** (SHA1 nova `bef773c9` / aria `054a17f3` · gate X2 verde en cada push).
- **PENDIENTE:** Fase 2 (orquestación estructurada REAL — handoffs hoy inertes + chains que colapsan a NOVA — + autoconciencia/tool-use de capacidades) · Fase 3 (loop P5 `was_correct` para NOVA · hoy solo cableado para ARIA).

### Deudas nuevas registradas Sesión 5 (NO ejecutadas)
- **DEBT-NOVA-CHAT-HTTPX-DIRECT** 🟠 — el NOVA path (`chat.py`) llama a Claude vía `httpx` directo en vez de `anthropic_adapter` (se salta cache_control/routing_table/HERMES/Result-tuple · deuda I1/I3). Migrar al adapter. Absorbe la limpieza del param `temperature` inerte que quedó en `chat.py` y `anthropic_provider.py`.
- **DEBT-NOVA-IDENTITY-F1.5** 🟡 — 6 islas de nombres legacy fuera del núcleo reconciliado en F1: `tool_registry.py`, `agent_memory_service.py` (lista MAYA/SARA/MALU/LOLA/DANI aún más vieja), `prompt_vault` (default `RAFA`), `content_lab` mappings (`RAFA→REX`), `execute_agent_agentic.py`. Repuntar al canónico (`resolve_alias`).
- **DEBT-OMEGA-DEPARTMENTS-TABLE-MISSING** 🟡 — `get_briefing` sección `departments` consulta `omega_departments` (tabla muerta · NO EXISTE en prod · distinta de `omega_agents`). Repuntar a un origen real o quitar la sección.
- **DEBT-GATE-PYTEST-FALSE-GREEN** 🟠 — CHECK 9 de `scripts/validate-before-push.sh` es FALSO-VERDE por bug de shell (`pytest | tail | grep` + `set -o pipefail`: el exit 1 de pytest domina el pipeline → el `if` lo lee como "no falló" → `print_pass`). Un pytest que falla NO bloquea el push. Fix: capturar el exit code directo (`if (cd backend && pytest -q --tb=no >/dev/null 2>&1); then pass else fail`).
