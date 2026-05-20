-- ═══════════════════════════════════════════════════════════════════
-- OmegaRaisen — Migración 00008: ARIA Intelligence schema (Fase 1)
-- · ARIA_NOVA_INTELLIGENCE.md §9 · 5 tablas + 2 ALTERs
-- · behavioral_events + brand_voice_corpus + aria_conversations
--   (cliente ve sus propios datos · RLS por user_id/client_id)
-- · cross_client_benchmarks + aria_nba_log (service_role only · privacy)
-- · ALTER clients (industry/region/aria_level)
-- · ALTER agent_memory (source_event_id/aria_nba_id) · trazabilidad
-- ═══════════════════════════════════════════════════════════════════

-- ─── 1. ALTER clients · cross-client intelligence cols ────────────
ALTER TABLE clients
  ADD COLUMN IF NOT EXISTS industry   text,
  ADD COLUMN IF NOT EXISTS region     text,
  ADD COLUMN IF NOT EXISTS aria_level integer DEFAULT 1
    CHECK (aria_level BETWEEN 1 AND 4);

-- ─── 2. behavioral_events · prioridad 1 · 19+ event_types ─────────
-- event_types canónicos (no CHECK strict · permite agregar sin migración):
--   feature_open, content_approved, content_rejected, content_modified,
--   inactivity_3d, inactivity_7d, feature_bounce, consumption_alert_80,
--   consumption_alert_95, account_connected, plan_upgraded, aria_opened,
--   aria_suggestion_ignored, aria_suggestion_approved, post_published,
--   post_failed, analytics_viewed, calendar_used, media_generated
CREATE TABLE IF NOT EXISTS behavioral_events (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id   uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  user_id     uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  event_type  text NOT NULL,
  event_data  jsonb,
  session_id  uuid,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_behavioral_events_client_created
  ON behavioral_events (client_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_behavioral_events_user_created
  ON behavioral_events (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_behavioral_events_type
  ON behavioral_events (event_type);

ALTER TABLE behavioral_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "behavioral_events service role full"
  ON behavioral_events FOR ALL
  USING (auth.role() = 'service_role');

-- Cliente ve sus propios eventos (Q2:B · R5 transparencia)
CREATE POLICY "behavioral_events client view own"
  ON behavioral_events FOR SELECT
  USING (client_id IN (
    SELECT id FROM clients WHERE user_id = (SELECT auth.uid())
  ));

-- ─── 3. brand_voice_corpus · prioridad 2 · ivfflat embedding ──────
CREATE TABLE IF NOT EXISTS brand_voice_corpus (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id        uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  text             text NOT NULL,
  tone_tags        text[] DEFAULT '{}',
  platform         text,
  engagement_score float,
  source           text CHECK (source IN ('approved_draft','manual_upload','top_performing_post')),
  embedding        vector(1536),
  created_at       timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_brand_voice_corpus_client
  ON brand_voice_corpus (client_id);
CREATE INDEX IF NOT EXISTS idx_brand_voice_corpus_embedding
  ON brand_voice_corpus USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

ALTER TABLE brand_voice_corpus ENABLE ROW LEVEL SECURITY;

CREATE POLICY "brand_voice_corpus service role full"
  ON brand_voice_corpus FOR ALL
  USING (auth.role() = 'service_role');

-- Cliente ve su propio corpus (Q3:B · es SU material aprobado)
CREATE POLICY "brand_voice_corpus client view own"
  ON brand_voice_corpus FOR SELECT
  USING (client_id IN (
    SELECT id FROM clients WHERE user_id = (SELECT auth.uid())
  ));

-- ─── 4. aria_conversations · prioridad 3 · historial completo ─────
CREATE TABLE IF NOT EXISTS aria_conversations (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  client_id  uuid REFERENCES clients(id) ON DELETE SET NULL,
  role       text NOT NULL CHECK (role IN ('user','assistant')),
  content    text NOT NULL,
  aria_level integer CHECK (aria_level BETWEEN 1 AND 4),
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Index ASC para orden cronológico (history endpoint últimos 50 ASC)
CREATE INDEX IF NOT EXISTS idx_aria_conversations_user_created
  ON aria_conversations (user_id, created_at ASC);

ALTER TABLE aria_conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "aria_conversations service role full"
  ON aria_conversations FOR ALL
  USING (auth.role() = 'service_role');

-- User (cliente o reseller) ve su propia conversación
CREATE POLICY "aria_conversations user view own"
  ON aria_conversations FOR SELECT
  USING (user_id = (SELECT auth.uid()));

-- ─── 5. cross_client_benchmarks · prioridad 4 · k-anonymity 5+ ────
CREATE TABLE IF NOT EXISTS cross_client_benchmarks (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  industry         text NOT NULL,
  region           text NOT NULL,
  metric_name      text NOT NULL,
  metric_value     float NOT NULL,
  metric_unit      text,
  sample_size      integer NOT NULL CHECK (sample_size >= 5),
  confidence_score float,
  valid_from       date NOT NULL,
  valid_to         date,
  created_at       timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cross_client_benchmarks_industry_region
  ON cross_client_benchmarks (industry, region, metric_name);

ALTER TABLE cross_client_benchmarks ENABLE ROW LEVEL SECURITY;

-- Service_role only · privacy by design (clientes nunca ven raw benchmarks)
CREATE POLICY "cross_client_benchmarks service role only"
  ON cross_client_benchmarks FOR ALL
  USING (auth.role() = 'service_role');

-- ─── 6. aria_nba_log · prioridad 5 · audit NBA engine ─────────────
CREATE TABLE IF NOT EXISTS aria_nba_log (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  trigger_events  jsonb,
  recommendation  text NOT NULL,
  nova_approved   boolean,
  nova_confidence integer CHECK (nova_confidence BETWEEN 0 AND 10),
  executed_at     timestamptz,
  outcome         text CHECK (outcome IN ('responded','ignored','converted','pending')),
  was_correct     boolean,
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_aria_nba_log_client_created
  ON aria_nba_log (client_id, created_at DESC);

ALTER TABLE aria_nba_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "aria_nba_log service role only"
  ON aria_nba_log FOR ALL
  USING (auth.role() = 'service_role');

-- ─── 7. ALTER agent_memory · trazabilidad behavioral + NBA ────────
ALTER TABLE agent_memory
  ADD COLUMN IF NOT EXISTS source_event_id uuid,
  ADD COLUMN IF NOT EXISTS aria_nba_id     uuid;
