# MCP_ARSENAL — OmegaRaisen
## Catálogo de MCPs, APIs y conectores del proyecto
### Firmados, aplicados y con activación por fase · Versión 1.0 · 17 mayo 2026

---

## QUÉ ES ESTE DOCUMENTO

Un MCP (Model Context Protocol) es un conector estándar que permite a Claude
interactuar con servicios externos de forma estructurada y auditada.

Este documento cataloga **todos** los MCPs, APIs y conectores del sistema
OmegaRaisen: cuáles están activos, cuáles están firmados para activación
futura, y cómo potencian cada componente del sistema.

> **Alcance:** Single-product multi-tenant white-label. Sin verticales
> (Aurora/Hera/Solaris no aplican). Sin tiers (Solo/Pro/Enterprise no
> aplican). Modelo de negocio: Reseller → Cliente final con branding propio.

---

## ESTADO ACTUAL (mayo 2026)

```
✅ ACTIVO       — instalado y funcionando en producción
⚙️  CONFIGURADO  — credenciales listas, pendiente de activación
⏳ FIRMADO      — decisión tomada, pendiente de implementación
🔵 FUTURO       — planificado, sin fecha confirmada
❌ DEPRECADO    — eliminado del stack por decisión owner
```

---

## CATEGORÍA 1 — MCPs DE DESARROLLO (Claude Code)

### 1.1 Supabase MCP ✅ ACTIVO

```
Propósito:    Claude Code lee y escribe en Supabase directamente
Usado en:     Desarrollo — migrations, RLS, queries de debugging
Configurado:  .claude/settings.json + SUPABASE_SERVICE_ROLE_KEY
Setup:        claude mcp add supabase --env SUPABASE_URL=$SUPABASE_URL \
                --env SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_ROLE_KEY

Herramientas que expone:
  supabase_query        → ejecutar SQL arbitrario
  supabase_list_tables  → introspección del schema
  supabase_describe     → ver estructura de tabla
  supabase_rpc          → llamar funciones Edge

Valor específico para OmegaRaisen:
  · Aplicar las 3 migraciones consolidadas (00001-00003) sin salir
    del terminal de Claude Code
  · Verificar RLS activa post-deploy: SELECT tablename FROM pg_tables
    WHERE rowsecurity=false AND ... — verificación automática
  · Insertar/leer agent_memory directamente durante refactor de agentes
  · Debugging de scheduled_posts, agent_log, content_lab_generated

Proyecto destino: rwlnihoqhxwpbehibgxu.supabase.co
```

### 1.2 GitHub MCP ✅ ACTIVO

```
Propósito:    Claude Code crea PRs, lee issues, gestiona branches
Configurado:  GITHUB_TOKEN (fine-grained, scopes repo+workflow)
              Repo único: github.com/raisenomega/Omega
Setup:        claude mcp add github --env GITHUB_TOKEN=$GITHUB_PAT

Herramientas que expone:
  github_create_pr       → abrir pull request con descripción
  github_list_issues     → ver issues abiertos
  github_create_issue    → crear issue desde Claude Code
  github_get_file        → leer archivo sin git clone

Valor específico para OmegaRaisen:
  · Cuando SENTINEL detecta crisis: Claude Code puede abrir issue
    automáticamente con stack trace + contexto del agente afectado
  · PRs por bounded context refactorizado (Fase 3 del MIGRATION_PLAN)
  · Verificación de identidad git: GitHub MCP confirma que el commit
    aparece firmado por raisenomega antes de mergear a main
```

### 1.3 Memory MCP ✅ ACTIVO · CRÍTICO

```
Propósito:    Persistir contexto de Claude Code entre sesiones
Configurado:  .claude/settings.json
Setup:        claude mcp add memory

Herramientas que expone:
  memory_store    → guardar decisión arquitectónica
  memory_retrieve → recuperar contexto de sesión anterior
  memory_list     → ver todas las memorias activas

Valor específico para OmegaRaisen:
  · Resuelve el problema raíz: cada sesión nueva arranca ciega,
    re-pregunta las mismas decisiones, re-discute las excepciones
    de I1, re-explica por qué Nano Banana en lugar de DALL-E
  · Con Memory MCP, Claude Code recuerda:
      - Qué agentes están migrados a bc_cognition V3
      - Por qué se eligió Anthropic único + 2 excepciones Google
      - Qué SHA1 tiene limits_omega.py (ee472c1d...)
      - Qué decisiones tomó el owner el 17 may 2026

⚠ NOTA CRÍTICA: sin Memory MCP activo, se repiten los errores entre
sesiones. Verificar que esté activo en CADA sesión nueva antes de
empezar trabajo técnico.
```

### 1.4 Context7 MCP ✅ ACTIVO

```
Propósito:    Documentación actualizada de librerías en tiempo real
Configurado:  .claude/settings.json
Setup:        claude mcp add context7

Herramientas que expone:
  context7_docs  → docs actuales de FastAPI, Anthropic SDK,
                   google-genai, Vite, Supabase Python SDK, etc.

Valor específico para OmegaRaisen:
  · Claude Code no usa documentación de entrenamiento (puede estar
    desactualizada). Context7 garantiza que el código generado usa:
      - anthropic >=0.34 (cache_control: ephemeral correcto)
      - google-genai (SDK nuevo, NO google-generativeai)
      - FastAPI 0.109 patterns
      - Pydantic 2 (no v1 deprecated syntax)
  · Crítico al refactorizar los 22 agentes — evita usar APIs viejas
```

---

## CATEGORÍA 2 — MCPs DE CANALES SOCIALES

### 2.1 Meta Ads MCP Oficial ⚙️ CONFIGURADO — Fase 3

```
Qué es:       MCP oficial de Meta para campañas y analytics pagadas
              Lanzado en open beta: 29 abril 2026
URL oficial:  mcp.facebook.com/ads   +   mcp.meta.com/ads/<business-id>
Credenciales: NINGUNA — autenticación OAuth estándar Business Suite
              (mismo login de Business Manager · sin Developer App · sin App Review)
Setup:        En .claude/settings.json:
                {
                  "mcpServers": {
                    "meta-ads": { "url": "https://mcp.facebook.com/ads" }
                  }
                }
              Luego: abre Claude → OAuth flow → autorizar Business Account
              ⚠️ BUG CONOCIDO en Claude Code: OAuth falla con
                "redirect_uris not registered" — usar Claude Desktop o
                claude.ai web para la auth inicial (workaround confirmado).
              ALTERNATIVA en terminal: Meta Ads CLI
                npm install -g @meta/ads-cli
                meta login    (OAuth)
                meta campaigns list --account-id act_XXXXX

29 herramientas que expone:
  analytics:    ads_insights_performance_trend, ads_insights_anomaly_signal,
                ads_insights_auction_ranking_benchmarks, ads_insights_industry_benchmark
  campañas:     ads_get_ad_accounts, ads_get_ad_entities (campaigns/ad sets/ads),
                ads_create_campaign, ads_create_adset, ads_create_ad
  operaciones:  ads_update_entity (budgets, targeting, schedules),
                ads_activate_pause_entity
  catálogos:    ads_catalog_get_catalogs, ads_catalog_get_products,
                ads_catalog_get_diagnostics
  dataset:      ads_get_dataset_quality, ads_get_dataset_stats, ads_get_errors

Flujo con bc_cognition:
  analytics (Sonnet) consulta ads_insights_performance_trend por cliente
    → consolida métricas reales en reseller_dashboard.health
    → was_correct se actualiza en agent_memory basado en engagement real
    → ORACLE usa estos datos en el brief ejecutivo de los lunes

Lo que NO cubre este MCP (sigue requiriendo Developer App):
  · Publicar posts orgánicos en Instagram Feed / Facebook / Stories
  · WhatsApp Business broadcasts
  → Ver §2.2 para esa capa
```

### 2.2 Meta Content Publishing API ⏳ FIRMADO — Fase 3 (post-Developer App approval)

```
Tipo:         Custom adapter — requiere Meta Developer App + App Review
              (esto es lo que era DEBT-003)
Credenciales: META_APP_ID + META_APP_SECRET + META_ACCESS_TOKEN
              INSTAGRAM_APP_ID + INSTAGRAM_APP_SECRET
Vive en:      backend/app/infrastructure/integrations/meta_publisher.py
              (NO en bc_cognition — es publicación, no cognición)

Herramientas que expondrá (post-aprobación):
  meta_publish_post        → publicar en Instagram Feed/Facebook orgánico
  meta_publish_reel        → publicar Reel orgánico
  meta_publish_story       → publicar Story orgánico
  whatsapp_send_template   → broadcast opt-in (templates Meta-aprobados)

Estado: DEBT-003 sigue activo para esta capa.
        La Capa 1 (§2.1 Meta Ads MCP) ya no está bloqueada — analytics
        y campañas pagadas disponibles sin Developer App.
Activación: cuando bc_cognition tenga content_creator + orchestrator
            + brand_voice_checker en V3 (Fase 3) Y Meta App esté aprobada.
```

### 2.2 TikTok Business API ⏳ FIRMADO — Fase 3

```
Tipo:         Custom adapter (no MCP oficial todavía)
Credenciales: TIKTOK_APP_ID + TIKTOK_APP_SECRET + TIKTOK_ACCESS_TOKEN
Vive en:      backend/app/infrastructure/integrations/tiktok_adapter.py

Herramientas que expondrá:
  tiktok_upload_video    → subir video corto
  tiktok_get_analytics   → métricas de TikTok

Flujo con bc_cognition:
  video_prompt_writer (Sonnet) construye prompt cinematográfico
    → veo3_adapter genera video (8s, 1080p, audio nativo)
    → tiktok_adapter.publish(video_uri, caption, hashtags)
    → analytics (Sonnet) trackea retención y ajusta duración del siguiente

Estado bloqueante: DEBT-003 (sin TikTok Business approval aún).
```

### 2.3 LinkedIn API 🔵 FUTURO — Mes 3+

```
Tipo:         Custom adapter
Credenciales: LINKEDIN_CLIENT_ID + LINKEDIN_CLIENT_SECRET
Vive en:      backend/app/infrastructure/integrations/linkedin_adapter.py

Valor para OmegaRaisen:
  Resellers que operan cuentas B2B de sus clientes necesitan LinkedIn.
  Tier de prioridad bajo hasta que ≥10% de clientes pidan.
```

### 2.4 YouTube Data API 🔵 FUTURO — Mes 4+

```
Tipo:         Custom adapter (vía Google Cloud Console)
Credenciales: GOOGLE_OAUTH_CLIENT_ID + GOOGLE_OAUTH_CLIENT_SECRET
Vive en:      backend/app/infrastructure/integrations/youtube_adapter.py

Herramientas que expondrá:
  youtube_upload_video       → subir video largo a YouTube
  youtube_publish_short      → publicar YouTube Short
  youtube_get_analytics      → métricas de canal y video

Flujo con bc_cognition:
  Mismo patrón que TikTok — Veo 3.1 genera, YouTube publica.
```

### 2.5 Google Business Profile API 🔵 FUTURO — Mes 6+

```
Tipo:         Custom adapter
Credenciales: GOOGLE_OAUTH_CLIENT_ID + GBP_LOCATION_ID
Vive en:      backend/app/infrastructure/integrations/gbp_adapter.py

Valor para OmegaRaisen:
  Clientes con negocio local (PYMEs) necesitan gestionar reseñas
  y posts de Google Business. crisis_manager detecta reseñas
  negativas y propone respuesta draft.
```

---

## CATEGORÍA 3 — MCPs DE MEDIA (DENTRO de bc_cognition)

### 3.1 Nano Banana — Google Gemini Image ⚙️ CONFIGURADO

```
Qué es:       Excepción documentada de DDD I1 — generación de imágenes
              Aprobado por owner 17 may 2026 (re-evaluación Q4 2026)
SDK:          google-genai (NO google-generativeai legacy)
Credenciales: GEMINI_API_KEY (única key cubre Nano Banana + Veo 3.1)
Vive en:      backend/app/bc_cognition/infrastructure/nano_banana_adapter.py
              (ÚNICO archivo que importa google.genai para imágenes)

Modelos permitidos:
  gemini-3.1-flash-image-preview     ⭐ DEFAULT (Nano Banana 2)
  gemini-3-pro-image-preview         Premium (texto en imagen, diagramas)
  gemini-2.5-flash-image             Legacy bulk (alto volumen barato)

Por qué Nano Banana (no DALL-E):
  ✓ Mejor texto dentro de imagen (fechas, precios, nombres)
  ✓ Character consistency entre generaciones (brand assets recurrentes)
  ✓ Mejor representación de tonos de piel sin sesgo
  ✓ Costo ~$0.039/imagen vs $0.04-$0.08 DALL-E 3
  ✓ Velocidad ~3s vs 8-15s DALL-E 3
  ✓ Watermark SynthID nativo (requisito legal — documentar en TOS cliente)

Flujo con bc_cognition:
  content_creator (Sonnet) construye brief visual
    → image_prompt_writer (Sonnet) refina prompt
    → nano_banana_adapter.generate(prompt, route="default", aspect_ratio)
    → returns ImageResponse(image_b64, mime_type, model_used, latency_ms)
    → o ImageError(code, message) — nunca lanza
    → bc_cognition guarda imagen en Supabase Storage bucket reseller-media
    → URL signed retornada al frontend

Formatos producidos:
  1:1   → Instagram post cuadrado (1080×1080)
  4:5   → Instagram post vertical (mayor alcance · 1080×1350)
  16:9  → Facebook + YouTube thumbnail (1200×630)
  9:16  → Stories + TikTok + Reels (1080×1920)
  21:9  → Hero banners web

Activación: incluida en Fase 2 del MIGRATION_PLAN (hot-swap DALL-E → Nano Banana)
```

### 3.2 Veo 3.1 — Google Vertex AI / GenAI ⚙️ CONFIGURADO

```
Qué es:       Excepción documentada de DDD I1 — generación de video
              Aprobado por owner 17 may 2026 (re-evaluación Q4 2026)
SDK:          google-genai (misma key que Nano Banana)
Credenciales: GEMINI_API_KEY
Vive en:      backend/app/bc_cognition/infrastructure/veo3_adapter.py
              (ÚNICO archivo que importa google.genai para video)

Modelos permitidos:
  veo-3.1-generate-preview            ⭐ DEFAULT (8s · 1080p · audio nativo)
  veo-3.1-lite-generate-preview       Cheap (50% costo, mismo speed)

Por qué Veo 3.1:
  ✓ Audio sincronizado nativo (Sora/Kling no tienen)
  ✓ Calidad cinematográfica
  ✓ Instrucciones en español
  ✓ Personajes consistentes entre tomas
  ✓ Único reemplazo viable para Runway/FAL (ambos eliminados del stack)

Costo:         ~$1-$3 por video de 8s
Latencia:      30-90s (long-running operation — start + poll pattern)

Flujo con bc_cognition (LRO async):
  video_prompt_writer (Sonnet) construye script estructurado
    → veo3_adapter.start_generation(prompt, route="default", aspect_ratio="9:16")
    → returns VideoOperation(operation_name, model_used, started_at)
    → Worker async hace polling cada 10s:
        veo3_adapter.poll(operation, max_wait_s=300, poll_interval_s=10)
    → returns VideoResult(video_uri, duration_s=8, has_audio=True, ...)
    → bc_channels descarga URI antes de TTL (Google expira URLs)
    → Sube a Supabase Storage + actualiza scheduled_posts

Activación: incluida en Fase 2 del MIGRATION_PLAN (hot-swap Runway/FAL → Veo 3.1)
```

### 3.3 DALL-E 3 ❌ DEPRECADO (17 may 2026)

```
Estado:    Eliminado del stack por decisión owner
Razón:     Nano Banana lo supera en calidad, costo, velocidad y consistencia.
Acción:    Remover backend/app/infrastructure/ai/openai_service.py
           Eliminar OPENAI_API_KEY de Railway + Vercel envs.
           Revocar key en OpenAI Console (proactivo · capa 1 seguridad).
```

### 3.4 Runway / FAL ❌ DEPRECADO (17 may 2026)

```
Estado:    Eliminados del stack por decisión owner
Razón:     Veo 3.1 los supera en audio nativo (Runway/FAL no tienen)
           y consistencia de personajes.
Acción:    Remover backend/app/agents/runway_agent.py
           Remover backend/app/agents/fal_video_agent.py
           Eliminar RUNWAYML_API_KEY, FAL_KEY de envs.
           Revocar ambas keys en consolas respectivas.
```

### 3.5 ElevenLabs (voz) 🔵 FUTURO — Año 2

```
Uso:     Voiceover para videos donde Veo 3.1 audio nativo no alcanza
         (narraciones largas, voces de marca específicas)
Valor:   Voz consistente de "narrador OmegaRaisen" sin grabar
Estado:  Sin prioridad — Veo 3.1 audio nativo cubre 90% de casos
```

---

## CATEGORÍA 4 — MCPs / APIs DE BÚSQUEDA Y CONTENIDO

### 4.1 Brave Search API ✅ ACTIVO

```
Qué es:       Motor de búsqueda con API limpia · reemplaza Tavily
Estado:       Activo desde commit 1e2ed99 (Wed Apr 8 2026)
Credenciales: BRAVE_API_KEY
Vive en:      backend/app/infrastructure/tools/web_search_tool.py

Usado por:
  trend_hunter (Sonnet)          → research de tendencias por industria
  competitive_intelligence       → análisis competitivo continuo
  news_monitor (cron 2h)         → noticias relevantes al cliente
  nova_chat (Opus)               → answer-engine cuando user pregunta cosas

Razón sobre Tavily: Brave Search más barato + sin filtro algorítmico
                    sesgado + mejor para mercado hispano + sin tracking.
```

---

## CATEGORÍA 5 — MCPs / APIs DE NEGOCIO

### 5.1 Stripe Connect ✅ ACTIVO

```
Estado:       Checkout + Customer Portal + Webhooks funcionando
              · Idempotencia verificada en webhook handler (DDD X4)
Credenciales: STRIPE_SECRET_KEY (sk_live_...) + STRIPE_WEBHOOK_SECRET
              Por env: dev usa sk_test_, prod usa sk_live_
Vive en:      backend/app/api/routes/billing/

Herramientas:
  stripe_create_checkout_session → iniciar pago de tier reseller
  stripe_create_connect_account  → onboarding de reseller nuevo
  stripe_create_subscription     → suscripción recurrente cliente final
  stripe_webhook_handler         → procesar eventos con idempotencia
                                   (tabla stripe_webhook_events con event.id PK)
  stripe_customer_portal         → cliente gestiona su suscripción

Flujo OmegaRaisen:
  Owner crea reseller en admin panel
    → stripe_create_connect_account → onboarding link
    → Reseller completa Stripe Onboarding
    → status="active" en tabla resellers
    → Reseller agrega clientes con sus propios precios
    → Stripe Connect mueve revenue: cliente paga → Stripe →
      reseller (90%) + OmegaRaisen platform fee (10%)
```

### 5.2 Resend (email transaccional) ✅ ACTIVO

```
Credenciales: RESEND_API_KEY
              EMAIL_FROM=no-reply@r-omega.agency
Vive en:      backend/app/infrastructure/email/resend_adapter.py

Templates en uso:
  · reseller_welcome              Bienvenida nuevo reseller
  · client_onboarded              Bienvenida cliente final del reseller
  · weekly_intel_brief            ORACLE brief semanal (lun 7 AM)
  · crisis_alert                  Alerta SENTINEL/crisis_manager
  · health_degradation            Cuando reseller_dashboard.health < verde
  · upsell_approved               Cliente solicitó agente extra · admin aprobó
```

---

## CATEGORÍA 6 — MCPs / APIs DE OBSERVABILIDAD

### 6.1 Langfuse ⚙️ CONFIGURADO — Activar Fase 4 (CRÍTICO)

```
Qué es:       Observabilidad completa de llamadas LLM
Credenciales: LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY (en .env)
Setup:        pip install langfuse en Fase 4 (descomentar en requirements.txt)
Vive en:      backend/app/bc_cognition/infrastructure/langfuse_observer.py
              + instrumentación en anthropic_adapter.py vía @observe

Qué captura por llamada a Claude / Nano Banana / Veo 3.1:
  · Prompt completo (system + user)
  · Respuesta completa
  · Tokens (input + output + cache_read)
  · Latencia ms
  · Modelo usado (claude-sonnet-4-6, etc.)
  · agent_code que llamó
  · client_id + reseller_id del request
  · was_correct cuando se actualiza (via agent_memory join)

Por qué es CRÍTICO:
  Sin Langfuse, OmegaRaisen opera ciego:
    - No sabe qué prompts funcionan
    - No sabe cuánto cuesta cada agente
    - No sabe dónde están los errores silenciosos
    - No puede A/B testear prompt evolution (DDD E3)
  Langfuse es el sistema nervioso de observabilidad.

Dashboard que provee:
  · Costo USD por agente por día (alerta si >$5/día/cliente)
  · P50/P95/P99 de latencia por modelo
  · Tasa de error por agente
  · Token efficiency: tokens por tipo de contenido
  · Cache hit rate (target ≥40% en system prompts con cache_control)
  · Comparación A/B de prompts (gate antes de mergear cambios)

Activación: Fase 4 del MIGRATION_PLAN_OMEGA (semana 8-9)
```

### 6.2 Sentry 🔵 FUTURO — opcional

```
Uso:      Errores frontend (Vite) + backend (FastAPI) en producción
Captura:  Excepciones no manejadas, errores de red, performance budget
Estado:   Sin prioridad — FastAPI global exception handler (main.py:175)
          + structlog cubren 80% de los casos. Langfuse cubre los LLM.
```

### 6.3 SENTINEL (interno) ✅ ACTIVO

```
No es MCP externo — es el sistema de monitoreo INTERNO de OmegaRaisen.
Cron pulse_monitor cada 5 min (main.py:75) verifica:
  · Tests passing en CI
  · Health de Railway (response time, error rate)
  · Cost por cliente bajo límites (MAX_USD_DIARIO_API_POR_CLIENTE)
  · Cero secretos en logs recientes
  · RLS activa en TODAS las tablas con identificador de propietario

Score < 95 → email + NOVA alert al owner.
Score ≥ 95 sostenido 7 días = métrica principal de éxito (regla X1).
```

---

## CATEGORÍA 7 — MCPs / APIs DE CALIDAD (dev tooling)

### 7.1 Promptfoo ⚙️ CONFIGURADO — Activar Fase 4

```
Uso:       Evaluar calidad de prompts antes de cambiarlos
Comando:   npx promptfoo eval
Regla:     DDD T2 — ejecutar antes de tocar cualquier system prompt
Config:    promptfoo.yaml en raíz del repo

Evals planificados (Fase 4):
  eval-content-creator      caption tiene CTA, tono correcto, hashtags
  eval-strategy             calendario tiene fechas, plataformas, horarios
  eval-brand-voice          retorna JSON con score ≥ 0.7 cuando match
  eval-crisis-manager       NUNCA responde directamente, siempre draft
  eval-nova-chat            persona consistente entre conversaciones

Gate de CI: cualquier cambio en domain/persona_*.py debe pasar
            promptfoo eval con regresión < 5% vs baseline.
```

---

## RESUMEN — ACTIVACIÓN POR FASE

(Alineado con `MIGRATION_PLAN_OMEGA.md`)

```
═══ FASE 0 (HOY · documentos fundacionales entregados) ═══
  ✅ Supabase MCP        — para aplicar las 3 migraciones SQL
  ✅ GitHub MCP          — repo raisenomega/Omega ya creado
  ✅ Memory MCP          — CRÍTICO entre sesiones
  ✅ Context7 MCP        — docs FastAPI + anthropic + google-genai

═══ FASE 1 (1-2 días · infraestructura nueva) ═══
  ✅ Brave Search API    — ya activo, migrar key al nuevo Railway
  ✅ Stripe Connect      — ya activo, migrar webhooks al nuevo Railway
  ✅ Resend              — ya activo, migrar al nuevo entorno

═══ FASE 2 (5-7 días · lift & shift + swap proveedores) ═══
  ⚙️ Nano Banana         — ACTIVAR · hot-swap DALL-E 3 → Nano Banana
  ⚙️ Veo 3.1             — ACTIVAR · hot-swap Runway/FAL → Veo 3.1
  ❌ DALL-E 3            — DEPRECAR · revocar key OpenAI
  ❌ Runway              — DEPRECAR · revocar key
  ❌ FAL                 — DEPRECAR · revocar key
  ❌ OpenAI text         — DEPRECAR (todo el texto va a Anthropic)
  ❌ Groq                — DEPRECAR · revocar key
  ❌ DeepSeek            — DEPRECAR · revocar key

═══ FASE 3 (4-6 semanas · refactor DDD a bc_cognition) ═══
  ⚙️ Meta Ads MCP Oficial  — ACTIVAR (sin Developer App · OAuth Business Suite)
                              analytics + campañas pagadas Instagram/Facebook
  ⏳ Meta Content Publishing — sigue esperando Developer App approval (DEBT-003)
  ⏳ TikTok Business API    — activar cuando TikTok approval llegue
  · No requiere MCPs nuevos · refactor de agentes existentes

═══ FASE 4 (1-2 semanas · auto-evolución + observabilidad) ═══
  ⚙️ Langfuse           — ACTIVAR (CRÍTICO antes de prompt evolution)
  ⚙️ Promptfoo          — ACTIVAR como gate en CI

═══ MES 3+ ═══
  🔵 LinkedIn API        — si ≥10% de clientes B2B lo piden

═══ MES 4-6+ ═══
  🔵 YouTube Data API    — videos largos para resellers con clientes EDU
  🔵 Google Business     — gestión de reseñas y posts locales

═══ AÑO 2+ ═══
  🔵 ElevenLabs          — voiceover si Veo audio nativo no alcanza
  🔵 Sentry              — si Langfuse + global handler no son suficientes
```

---

## POTENCIAL REAL — OMEGARAISEN COMPLETO

Los 37 agentes IA de bc_cognition + los MCPs activados según la fase
correspondiente = sistema que:

```
CONTENT_CREATOR + Nano Banana + Meta API
  → Genera caption + imagen alineada a brand voice
  → Valida contra brand_voice_checker (score ≥ 0.7)
  → Publica en Instagram con confidence ≥ 7
  → 24h después: analytics consulta engagement real
  → was_correct updateado en agent_memory → modelo aprende

VIDEO_PROMPT_WRITER + Veo 3.1 + TikTok API
  → Script estructurado (hook, scenes, cta)
  → veo3_adapter.start_generation (LRO async)
  → Worker poll cada 10s hasta done
  → tiktok_adapter.publish con caption
  → analytics mide retención y ajusta duración

STRATEGY + Brave Search + Analytics
  → Investiga tendencias del nicho del cliente
  → Cruza con histórico de mejor engagement del cliente
  → Genera calendario editorial con slots óptimos

CRISIS_MANAGER (Opus) + Resend + NOVA chat
  → Detecta sentiment_score < 0.3 en comments/mentions
  → NUNCA responde solo (regla P4)
  → Genera draft de respuesta para revisión humana
  → resend_adapter envía alerta + NOVA notifica chat
  → Owner aprueba → meta_adapter publica respuesta

ORACLE (Opus, cron lun 7AM) + Langfuse
  → Cruza datos de 7 días (publicación, engagement, costo)
  → Síntesis ejecutiva con Claude Opus
  → INSERT en oracle_briefs
  → Resend envía brief al owner

SENTINEL (cron 5 min) + Supabase MCP
  → SELECT FROM agent_log para detectar errores
  → SELECT FROM agent_memory para detectar drift
  → Verifica RLS activa en TODAS las tablas
  → Score ≥ 95 sostenido = regla X1 cumplida
```

---

## REGLAS DE USO DE MCPs / APIs

```
R1 — Ningún MCP se activa sin credenciales en .env y prueba local
R2 — Meta Ads MCP (§2.1): OAuth Business Suite · sin App ID/Secret requeridos
     Activa análisis + campañas pagadas. Para publicación orgánica: ver R2b.
R2b — Meta Content Publishing (§2.2): NUNCA publicar sin consent verificado
     del cliente (clients.consent_publishing_active = true). Requiere
     META_APP_ID + META_APP_SECRET en .env (solo cuando Developer App aprobada).
R3 — WhatsApp: NUNCA broadcast a lista sin opt-in firmado individualmente
     (tabla leads.consent_given = true + consent_date NOT NULL)
R4 — Langfuse: OBLIGATORIO antes de activar Meta API en producción
     (necesitamos observabilidad antes de publicar en redes reales)
R5 — Veo 3.1: verificar tier del reseller antes de generar (costo ~$2/video)
     Reseller que excede MAX_USD_DIARIO_API_POR_CLIENTE → degradar a Nano Banana imagen
R6 — bc_cognition es la ÚNICA capa con SDK de IA externo
     · anthropic SDK → SOLO anthropic_adapter.py
     · google.genai SDK → SOLO nano_banana_adapter.py + veo3_adapter.py
     · Cualquier otro intento de import → push bloqueado (DDD I1 + I10)
R7 — Stripe webhook: SIEMPRE verificar event.id contra stripe_webhook_events
     antes de procesar (idempotencia · DDD X4)
R8 — Memory MCP: verificar activo al inicio de cada sesión Claude Code
     · Sin Memory MCP = se repiten errores entre sesiones
```

---

## CONTRASTE CON LA VERSIÓN UNIVERSAL

Este documento adapta `MCP_ARSENAL_OMEGA.md` (universal multi-vertical)
a la realidad OmegaRaisen:

```
UNIVERSAL                              OMEGARAISEN
─────────────────────────────────      ─────────────────────────────────
Multi-vertical (Aurora/Hera/Solaris)   Single-product multi-tenant white-label
Tiers Solo/Pro/Network/Enterprise      Reseller plans + per-client upsells
Repo monorepo raisen-omega             Repo único raisenomega/Omega
Meta Ads MCP oficial Abril 2026        Custom adapter hasta MCP Meta listo
Google MCP oficial                     Custom adapters separados (YouTube + GBP)
DALL-E 3 como fallback                 DEPRECADO permanente (decisión owner)
gemini-2.5-flash-image                  gemini-3.1-flash-image-preview (Nano Banana 2)
Veo 3 (sin versión específica)         veo-3.1-generate-preview (default)
                                        + veo-3.1-lite-generate-preview (cheap)
TypeScript adapters (Hono)             Python adapters (FastAPI)
src/bc-channels/infrastructure/        backend/app/infrastructure/integrations/
src/bc-media/infrastructure/           backend/app/bc_cognition/infrastructure/
Sentry firmado                         Sentry futuro (Langfuse cubre 80%)
ElevenLabs futuro Año 2                Mantenido en futuro (Veo audio nativo cubre)
```

---

```
MCP_ARSENAL_OMEGA.md
Versión 1.0 · 17 mayo 2026
Aplica a: todo el repo raisenomega/Omega
Compatible con: BC_COGNITION_OMEGA.md + MIGRATION_PLAN_OMEGA.md + DDD_REGLAS_OMEGA.md
Reemplaza: MCP_ARSENAL_OMEGA.md (universal multi-vertical)
Próxima revisión: al cerrar Fase 2 (verificar Nano Banana + Veo 3.1 en producción)
```
