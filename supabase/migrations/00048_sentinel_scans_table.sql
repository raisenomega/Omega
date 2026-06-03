-- 00048_sentinel_scans_table.sql
-- Materializa la tabla per-agente que sentinel_service y handlers ya escriben/leen.
-- Resuelve DEBT-SENTINEL-BLIND (auditoría 2-jun) sin tocar código Python.
-- Patrón replica 00029 (sentinel_risk_scores · agregado).
-- Consumidores que se des-ciegan: get_status, get_history, deploy_check, oracle:43, get_briefing:55, _dept_report.
-- Bonus: arregla latent 500 de run_scan.py:62 (INSERT sin try/except).
-- Aditiva: cero DROP · CREATE TABLE IF NOT EXISTS.

-- ─── sentinel_scans · una fila por scan de agente (VAULT/PULSE/DB_GUARDIAN) ──
CREATE TABLE IF NOT EXISTS sentinel_scans (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_code       text NOT NULL,                  -- VAULT, PULSE, DB_GUARDIAN, etc.
  scan_type        text NOT NULL,                  -- "full", "quick", "manual", etc.
  status           text NOT NULL,                  -- "pass", "fail", "warning"
  security_score   integer,                        -- 0-100 · nullable (algunos scans no lo calculan)
  issues           jsonb NOT NULL DEFAULT '[]'::jsonb,   -- array de issues detectados
  deploy_decision  text,                           -- "approve"/"block"/"warn" · nullable
  scan_duration_ms integer,                        -- nullable
  triggered_by     text,                           -- cron, manual, deploy · nullable
  auto_fixed       jsonb NOT NULL DEFAULT '[]'::jsonb,   -- fixes aplicados automáticos
  created_at       timestamptz NOT NULL DEFAULT now()
);

-- Índices · get_status/get_history/deploy_check ordenan por created_at DESC y filtran por agente/tipo.
CREATE INDEX IF NOT EXISTS idx_sentinel_scans_created_at ON sentinel_scans (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sentinel_scans_agent_code ON sentinel_scans (agent_code);
CREATE INDEX IF NOT EXISTS idx_sentinel_scans_scan_type  ON sentinel_scans (scan_type);

-- ─── RLS · solo service_role (tabla interna backend-only · sin acceso cliente) ──
ALTER TABLE sentinel_scans ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "sentinel_scans_service_role_all" ON sentinel_scans;
CREATE POLICY "sentinel_scans_service_role_all"
  ON sentinel_scans
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SELECT manual en SQL Editor):
--   SELECT table_name FROM information_schema.tables
--     WHERE table_schema = 'public' AND table_name = 'sentinel_scans';
--   -- Esperado: 1 fila
--   SELECT count(*) FROM sentinel_scans;
--   -- Esperado: 0 (vacía tras migración · se llena en el próximo scan)
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00048
-- ═══════════════════════════════════════════════════════════════════
