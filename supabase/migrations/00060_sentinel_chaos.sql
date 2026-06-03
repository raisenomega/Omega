-- 00060_sentinel_chaos.sql
-- SENTINEL Sprint 2 · Capa 8 mínima (Chaos Engineering) · 13º componente.
-- Una fila por escenario por scan (comparten scanned_at + score overall). Worker 1er lunes/mes 3AM + on-demand.
-- Escenarios controlled + reversibles (in-process / read-only) · CERO daño a producción.
-- Reusa la función X4 sentinel_webhook_idempotency_enforced() de 00059. RLS service_role. Aditiva.

CREATE TABLE IF NOT EXISTS sentinel_chaos_scans (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scanned_at           timestamptz NOT NULL DEFAULT now(),
  scenario             text NOT NULL,
  result               text NOT NULL CHECK (result IN ('passed', 'partial', 'failed', 'skipped')),
  response_observed    jsonb,
  expected_response    jsonb,
  recovery_time_ms     integer,
  graceful_degradation boolean,
  score                integer NOT NULL DEFAULT 100,   -- score overall del scan (igual en sus filas)
  issues               jsonb NOT NULL DEFAULT '[]'::jsonb,
  trigger_source       text CHECK (trigger_source IN ('cron', 'manual')),
  created_at           timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sentinel_chaos_created_at ON sentinel_chaos_scans (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sentinel_chaos_scenario  ON sentinel_chaos_scans (scenario, created_at DESC);

ALTER TABLE sentinel_chaos_scans ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "sentinel_chaos_service_role_all" ON sentinel_chaos_scans;
CREATE POLICY "sentinel_chaos_service_role_all"
  ON sentinel_chaos_scans
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply:  SELECT count(*) FROM sentinel_chaos_scans;  -- esperado 0
-- ═══════════════════════════════════════════════════════════════════
