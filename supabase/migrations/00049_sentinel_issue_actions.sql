-- 00049_sentinel_issue_actions.sql
-- Acciones del operador sobre issues de SENTINEL: Ignorar / despachar Fix.
-- issue_hash = sha256(severity|type|message) → identidad estable cross-scan.
-- RLS solo service_role (replica patrón sentinel_scans · 00048). Aditiva · CREATE IF NOT EXISTS.

CREATE TABLE IF NOT EXISTS sentinel_issue_actions (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id     uuid,                                            -- referencia opcional (puede ser NULL)
  agent_code  text NOT NULL,                                   -- VAULT / PULSE_MONITOR / DB_GUARDIAN
  issue_hash  text NOT NULL,                                   -- sha256(severity|type|message)
  action      text NOT NULL CHECK (action IN ('ignored', 'fix_dispatched')),
  user_id     uuid,                                            -- auth.users.id (Ibrain en V1)
  reason      text,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sentinel_issue_actions_hash ON sentinel_issue_actions (issue_hash);
CREATE INDEX IF NOT EXISTS idx_sentinel_issue_actions_created_at ON sentinel_issue_actions (created_at DESC);

ALTER TABLE sentinel_issue_actions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "sentinel_issue_actions_service_role_all" ON sentinel_issue_actions;
CREATE POLICY "sentinel_issue_actions_service_role_all"
  ON sentinel_issue_actions
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply:  SELECT count(*) FROM sentinel_issue_actions;  -- esperado 0
-- ═══════════════════════════════════════════════════════════════════
