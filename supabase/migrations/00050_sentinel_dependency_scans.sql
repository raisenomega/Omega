-- 00050_sentinel_dependency_scans.sql
-- Reportes del GitHub Action "SENTINEL Dependency Scan" (Capa 4 · CVEs/deps).
-- RLS solo service_role (replica patrón sentinel_scans/issue_actions). Aditiva.

CREATE TABLE IF NOT EXISTS sentinel_dependency_scans (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_type      text NOT NULL,                       -- "dependency"
  status         text NOT NULL,                       -- "passed" | "failed"
  summary        jsonb NOT NULL DEFAULT '{}'::jsonb,   -- {python, javascript, ...}
  github_run_id  text,
  created_at     timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sentinel_dependency_scans_created_at
  ON sentinel_dependency_scans (created_at DESC);

ALTER TABLE sentinel_dependency_scans ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "sentinel_dependency_scans_service_role_all" ON sentinel_dependency_scans;
CREATE POLICY "sentinel_dependency_scans_service_role_all"
  ON sentinel_dependency_scans
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);
