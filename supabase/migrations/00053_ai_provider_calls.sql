-- 00053_ai_provider_calls.sql
-- SENTINEL Capa 7-A · telemetría per-call del AIProviderRouter (Anthropic/Bedrock/Vertex).
-- Solo registra llamadas que pasan por el router (path canónico anthropic_adapter).
-- RLS solo service_role. Aditiva.

CREATE TABLE IF NOT EXISTS ai_provider_calls (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider    text NOT NULL CHECK (provider IN ('anthropic', 'bedrock', 'vertex')),
  model       text NOT NULL,
  agent_code  text,
  status      text NOT NULL CHECK (status IN ('success', 'failed', 'failover_triggered')),
  latency_ms  int,
  tokens_in   int,
  tokens_out  int,
  error       text,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_provider_calls_provider ON ai_provider_calls (provider, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_provider_calls_status   ON ai_provider_calls (status, created_at DESC);

ALTER TABLE ai_provider_calls ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "ai_provider_calls_service_role_all" ON ai_provider_calls;
CREATE POLICY "ai_provider_calls_service_role_all"
  ON ai_provider_calls FOR ALL TO service_role USING (true) WITH CHECK (true);
