-- ═══════════════════════════════════════════════════════════════════
-- OmegaRaisen — Migración 00002: Agent Memory + pgvector (DDD M1, M2, M5)
-- Crea infraestructura V3 obligatoria:
--   · agent_memory con embeddings vector(1536)
--   · agent_log para auditoría estructurada
--   · training_pairs preparada desde día 1
-- ═══════════════════════════════════════════════════════════════════

-- pgvector ya activada en 00001

-- ─── AGENT MEMORY (DDD M1) ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agent_memory (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  client_id     uuid REFERENCES clients(id) ON DELETE CASCADE,
  reseller_id   uuid REFERENCES resellers(id) ON DELETE CASCADE,
  agent_code    text NOT NULL,
  memory_type   text NOT NULL CHECK (memory_type IN ('episodic','semantic','procedural')),
  context       text NOT NULL,
  decision      text NOT NULL,
  reasoning     text,
  outcome       text,
  was_correct   boolean,
  confidence    integer NOT NULL CHECK (confidence BETWEEN 0 AND 10),
  embedding     vector(1536),                    -- DDD M2: pgvector
  metadata      jsonb DEFAULT '{}'::jsonb,
  created_at    timestamptz NOT NULL DEFAULT now(),
  evaluated_at  timestamptz,
  -- Verificable: cada decision queda atada a algún owner identifiable
  CONSTRAINT chk_owner_present
    CHECK (user_id IS NOT NULL OR client_id IS NOT NULL OR reseller_id IS NOT NULL)
);

CREATE INDEX idx_agent_memory_agent ON agent_memory(agent_code);
CREATE INDEX idx_agent_memory_client ON agent_memory(client_id);
CREATE INDEX idx_agent_memory_reseller ON agent_memory(reseller_id);
CREATE INDEX idx_agent_memory_type ON agent_memory(memory_type);
CREATE INDEX idx_agent_memory_was_correct ON agent_memory(was_correct);
CREATE INDEX idx_agent_memory_created ON agent_memory(created_at DESC);

-- Índice de similaridad vectorial (ivfflat, cosine distance)
CREATE INDEX idx_agent_memory_embedding
  ON agent_memory USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

ALTER TABLE agent_memory ENABLE ROW LEVEL SECURITY;

-- RLS: cada owner ve solo SU memoria
CREATE POLICY "Users read own memory"
  ON agent_memory FOR SELECT
  USING (
    user_id = auth.uid()
    OR client_id IN (SELECT id FROM clients WHERE user_id = auth.uid())
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  );

CREATE POLICY "Service role writes memory"
  ON agent_memory FOR INSERT WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role evaluates memory"
  ON agent_memory FOR UPDATE USING (auth.role() = 'service_role');

-- ─── AGENT LOG (DDD O2) ───────────────────────────────────────────
-- Log estructurado de cada llamada a agente (más granular que agent_memory)
CREATE TABLE IF NOT EXISTS agent_log (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_code      text NOT NULL,
  user_id         uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  client_id       uuid REFERENCES clients(id) ON DELETE SET NULL,
  request_id      uuid,                          -- correlation con tracing
  model_used      text NOT NULL,                 -- claude-haiku-4-5-20251001, etc.
  input_tokens    integer,
  output_tokens   integer,
  cost_usd        numeric(10,6),
  latency_ms      integer,
  cache_hit       boolean DEFAULT false,
  status          text NOT NULL CHECK (status IN ('success','error','timeout','rate_limited')),
  error_message   text,
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_agent_log_agent_time ON agent_log(agent_code, created_at DESC);
CREATE INDEX idx_agent_log_client ON agent_log(client_id);
CREATE INDEX idx_agent_log_status ON agent_log(status);

ALTER TABLE agent_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Owners view their agent logs"
  ON agent_log FOR SELECT
  USING (
    user_id = auth.uid()
    OR client_id IN (SELECT id FROM clients WHERE
      user_id = auth.uid()
      OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
    )
  );
CREATE POLICY "Service role writes agent logs"
  ON agent_log FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- ─── TRAINING PAIRS (DDD M5) ──────────────────────────────────────
-- Dataset de entrenamiento futuro: pares (input, expected_output) curados
CREATE TABLE IF NOT EXISTS training_pairs (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_memory_id uuid REFERENCES agent_memory(id) ON DELETE SET NULL,
  agent_code      text NOT NULL,
  input_context   text NOT NULL,
  expected_output text NOT NULL,
  quality_score   integer CHECK (quality_score BETWEEN 0 AND 10),
  curator_user_id uuid REFERENCES auth.users(id),
  curator_notes   text,
  is_active       boolean NOT NULL DEFAULT true,
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_training_pairs_agent ON training_pairs(agent_code);
CREATE INDEX idx_training_pairs_active ON training_pairs(is_active);
CREATE INDEX idx_training_pairs_quality ON training_pairs(quality_score DESC);

ALTER TABLE training_pairs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role only training pairs"
  ON training_pairs FOR ALL
  USING (auth.role() = 'service_role');

-- ─── HELPER FUNCTION: find similar memories ───────────────────────
CREATE OR REPLACE FUNCTION find_similar_memories(
  query_embedding vector(1536),
  target_agent_code text,
  target_client_id uuid DEFAULT NULL,
  limit_count integer DEFAULT 5,
  min_similarity float DEFAULT 0.7
)
RETURNS TABLE (
  id uuid,
  context text,
  decision text,
  reasoning text,
  was_correct boolean,
  confidence integer,
  similarity float
)
LANGUAGE sql
STABLE
AS $$
  SELECT
    m.id,
    m.context,
    m.decision,
    m.reasoning,
    m.was_correct,
    m.confidence,
    1 - (m.embedding <=> query_embedding) AS similarity
  FROM agent_memory m
  WHERE m.agent_code = target_agent_code
    AND (target_client_id IS NULL OR m.client_id = target_client_id)
    AND m.embedding IS NOT NULL
    AND 1 - (m.embedding <=> query_embedding) >= min_similarity
  ORDER BY m.embedding <=> query_embedding
  LIMIT limit_count;
$$;

-- ─── VISTA: estadísticas de rendimiento por agente ────────────────
CREATE OR REPLACE VIEW agent_performance_stats AS
SELECT
  agent_code,
  COUNT(*)                                                  AS total_decisions,
  COUNT(*) FILTER (WHERE was_correct = true)                AS correct_count,
  COUNT(*) FILTER (WHERE was_correct = false)               AS incorrect_count,
  COUNT(*) FILTER (WHERE was_correct IS NULL)               AS pending_evaluation,
  ROUND(
    COUNT(*) FILTER (WHERE was_correct = true)::numeric
    / NULLIF(COUNT(*) FILTER (WHERE was_correct IS NOT NULL), 0),
    3
  )                                                          AS accuracy_rate,
  AVG(confidence)                                            AS avg_confidence,
  AVG(CASE WHEN was_correct = true  THEN confidence END)     AS avg_confidence_when_correct,
  AVG(CASE WHEN was_correct = false THEN confidence END)     AS avg_confidence_when_wrong
FROM agent_memory
GROUP BY agent_code;

GRANT SELECT ON agent_performance_stats TO authenticated;

-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00002
-- ═══════════════════════════════════════════════════════════════════
