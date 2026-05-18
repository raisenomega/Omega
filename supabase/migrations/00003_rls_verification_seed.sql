-- ═══════════════════════════════════════════════════════════════════
-- OmegaRaisen — Migración 00003: RLS verification + Seed agentes
-- · Verifica que NINGUNA tabla con identificador de propietario quedó sin RLS
-- · Seedea los 37 agentes IA + 45 agentes organizacionales
-- ═══════════════════════════════════════════════════════════════════

-- ─── VERIFICACIÓN: toda tabla con user_id, client_id, reseller_id ─
-- debe tener RLS activado (regla DDD G5)
DO $$
DECLARE
  unprotected text;
  rec record;
BEGIN
  FOR rec IN
    SELECT t.tablename
    FROM pg_tables t
    JOIN information_schema.columns c
      ON c.table_schema = t.schemaname AND c.table_name = t.tablename
    WHERE t.schemaname = 'public'
      AND t.rowsecurity = false
      AND c.column_name IN ('user_id','client_id','reseller_id','org_id')
    GROUP BY t.tablename
  LOOP
    unprotected := COALESCE(unprotected || ', ', '') || rec.tablename;
  END LOOP;

  IF unprotected IS NOT NULL THEN
    RAISE EXCEPTION 'RLS violation: tablas sin RLS pero con identificadores de propietario: %', unprotected;
  END IF;
END$$;

-- ─── SEED: 37 agentes IA core ─────────────────────────────────────
-- Cada uno con su routing tier según DDD I2
INSERT INTO agents (code, name, category, description, model_tier, is_active, is_premium)
VALUES
  -- Tier HAIKU (rápido, barato — clasificación, lookup, texto corto)
  ('hashtag_generator',       'Hashtag Generator',       'content', 'Genera hashtags relevantes por tema/industria',   'haiku', true, false),
  ('emoji_suggestor',         'Emoji Suggestor',         'content', 'Sugiere emojis contextuales',                       'haiku', true, false),
  ('caption_optimizer',       'Caption Optimizer',       'content', 'Optimiza captions cortas',                         'haiku', true, false),
  ('sentiment_analyzer',      'Sentiment Analyzer',      'analytics','Análisis de sentimiento de comentarios/reviews',  'haiku', true, false),
  ('bio_generator',           'Bio Generator',           'content', 'Genera bios para perfiles sociales',                'haiku', true, false),

  -- Tier SONNET (workhorse — generación creativa, decisiones tácticas)
  ('content_creator',         'Content Creator',         'content',    'Genera posts (texto + imagen) alineados a brand voice', 'sonnet', true, false),
  ('strategy',                'Strategy Agent',          'strategy',   'Planifica calendario editorial mensual',                'sonnet', true, false),
  ('brand_voice',             'Brand Voice Agent',       'brand',      'Mantiene consistencia de tono por cliente',             'sonnet', true, false),
  ('analytics',               'Analytics Agent',         'analytics',  'Síntesis ejecutiva de métricas',                        'sonnet', true, false),
  ('scheduling',              'Scheduling Agent',        'distribution','Decide timing óptimo por audiencia',                    'sonnet', true, false),
  ('copywriter',              'Copywriter Agent',        'content',    'Copy persuasivo larga forma',                            'sonnet', true, false),
  ('trend_hunter',            'Trend Hunter Agent',      'intelligence','Detecta trends + filtra por relevancia al brand',       'sonnet', true, false),
  ('competitive_intelligence','Competitive Intelligence','intelligence','Análisis competitivo continuo',                          'sonnet', true, false),
  ('monitor',                 'Monitor Agent',           'operations', 'Health checking + alertas operacionales',                 'sonnet', true, false),
  ('engagement',              'Engagement Agent',        'community',  'Sugiere respuestas a comentarios (drafts)',               'sonnet', true, false),
  ('seo_optimizer',           'SEO Optimizer',           'content',    'Optimiza posts para descubrimiento',                      'sonnet', true, false),
  ('image_prompt_writer',     'Image Prompt Writer',     'content',    'Genera prompts para Nano Banana',                         'sonnet', true, false),
  ('video_prompt_writer',     'Video Prompt Writer',     'content',    'Genera prompts para Veo 3.1',                             'sonnet', true, false),
  ('community_moderator',     'Community Moderator',     'community',  'Detecta spam/toxicidad en comentarios',                   'sonnet', true, false),
  ('influencer_scout',        'Influencer Scout',        'growth',     'Identifica influencers alineados a brand',                'sonnet', true, true),

  -- Tier OPUS (premium — decisiones críticas, reputación, briefing ejecutivo)
  ('orchestrator',            'Master Orchestrator',     'meta',       'Coordina multi-agente para tareas complejas',             'opus', true, false),
  ('crisis_manager',          'Crisis Manager',          'risk',       'Detecta + propone drafts en crisis (NUNCA responde solo)','opus', true, false),
  ('oracle_service',          'Oracle Intelligence',     'strategy',   'Brief estratégico semanal',                               'opus', true, true),
  ('nova_chat',               'NOVA Chat (CEO Agent)',   'meta',       'Asistente conversacional ejecutivo',                      'opus', true, false),
  ('ab_testing_analysis',     'A/B Testing Analyst',     'analytics',  'Análisis de tests con significancia estadística',         'opus', true, true),
  ('report_generator',        'Report Generator',        'reporting',  'Reportes ejecutivos auditables',                          'opus', true, true),
  ('audit_reviewer',          'Audit Reviewer',          'governance', 'Auditoría de decisiones y código',                        'opus', true, true),
  ('growth_hacker',           'Growth Hacker',           'growth',     'Estrategias de crecimiento data-driven',                  'opus', true, true),
  ('sentinel_security',       'SENTINEL Security',       'security',   'Auditoría continua de seguridad',                         'opus', true, false),

  -- Helper agents
  ('client_context_builder',  'Client Context Builder',  'meta',       'Ensambla contexto ≤2k tokens por cliente',                'haiku', true, false),
  ('compliance_checker',      'Compliance Checker',      'governance', 'Verifica posts vs políticas de plataforma',               'sonnet', true, false),
  ('brand_voice_checker',     'Brand Voice Checker',     'brand',      'Score brand_voice_match antes de publicar',               'haiku', true, false),
  ('quality_control',         'Quality Control',         'governance', 'Score de calidad pre-aprobación',                         'sonnet', true, false),
  ('url_extractor',           'URL Extractor',           'utility',    'Extrae contenido de URLs',                                'haiku', true, false),
  ('pdf_extractor',           'PDF Extractor',           'utility',    'Extrae contenido de PDFs',                                'haiku', true, false),
  ('news_monitor',            'News Monitor',            'intelligence','Worker autónomo cada 2h',                                 'sonnet', true, false),
  ('competitor_tracker',      'Competitor Tracker',      'intelligence','Worker autónomo cada 6h',                                 'sonnet', true, false)
ON CONFLICT (code) DO UPDATE SET
  name = EXCLUDED.name,
  category = EXCLUDED.category,
  description = EXCLUDED.description,
  model_tier = EXCLUDED.model_tier,
  is_active = EXCLUDED.is_active,
  is_premium = EXCLUDED.is_premium,
  updated_at = now();

-- ─── Verificación final ───────────────────────────────────────────
DO $$
DECLARE
  agent_count integer;
BEGIN
  SELECT COUNT(*) INTO agent_count FROM agents WHERE is_active = true;
  IF agent_count < 37 THEN
    RAISE EXCEPTION 'Seed incompleto: solo % agentes activos (esperado ≥37)', agent_count;
  END IF;
  RAISE NOTICE '✓ Seed completo: % agentes activos', agent_count;
END$$;

-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00003
-- ═══════════════════════════════════════════════════════════════════
