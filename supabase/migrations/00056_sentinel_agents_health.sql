-- 00056_sentinel_agents_health.sql
-- SENTINEL Capa 12 · salud de agentes IA. Fuente = ai_provider_calls (agent_log vacío) + agent_memory.
-- RLS service_role. Aditiva.

CREATE TABLE IF NOT EXISTS sentinel_agents_health_scans (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scanned_at           timestamptz,
  per_agent            jsonb NOT NULL DEFAULT '[]'::jsonb,
  model_drift_alerts   jsonb NOT NULL DEFAULT '[]'::jsonb,
  total_daily_cost_usd numeric,
  cost_calculation_source text,
  score                int NOT NULL DEFAULT 100,
  issues               jsonb NOT NULL DEFAULT '[]'::jsonb,
  coverage_note        text,
  created_at           timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sentinel_agents_health_created ON sentinel_agents_health_scans (created_at DESC);

ALTER TABLE sentinel_agents_health_scans ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "sentinel_agents_health_service_role_all" ON sentinel_agents_health_scans;
CREATE POLICY "sentinel_agents_health_service_role_all"
  ON sentinel_agents_health_scans FOR ALL TO service_role USING (true) WITH CHECK (true);
