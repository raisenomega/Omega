-- 00057_sentinel_issue_actions_extend.sql
-- Sub-bloque B · generaliza sentinel_issue_actions a issues de las 10 fuentes SENTINEL.
-- source_type identifica la fuente (sentinel_scan = retro-compat de filas existentes).
-- source_id apunta al scan/audit de la tabla origen (puede ser NULL para fuentes sin id estable).
-- NOTA: agent_code NO tiene CHECK (verificado en 00049 · es text libre) → nada que dropear.
-- Aditiva · idempotente (ADD COLUMN IF NOT EXISTS).

ALTER TABLE sentinel_issue_actions
  ADD COLUMN IF NOT EXISTS source_type text NOT NULL DEFAULT 'sentinel_scan';

ALTER TABLE sentinel_issue_actions
  ADD COLUMN IF NOT EXISTS source_id uuid;

CREATE INDEX IF NOT EXISTS idx_sentinel_issue_actions_source
  ON sentinel_issue_actions (source_type, source_id);

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply:
--   SELECT column_name FROM information_schema.columns
--     WHERE table_name='sentinel_issue_actions' AND column_name IN ('source_type','source_id');
--   -- Esperado: 2 filas
--   SELECT source_type, count(*) FROM sentinel_issue_actions GROUP BY source_type;
--   -- Esperado: filas existentes con source_type='sentinel_scan'
-- ═══════════════════════════════════════════════════════════════════
