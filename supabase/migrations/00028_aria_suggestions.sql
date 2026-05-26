-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00028 · aria_suggestions                              ║
-- ║  26 may 2026 · ARIA Intelligence · Next-Best-Action proactivo    ║
-- ║                                                                   ║
-- ║  Propósito: sugerencias proactivas que ARIA genera por cliente    ║
-- ║   inactivity · upgrade_plan · profile_incomplete · no_addons     ║
-- ║                                                                   ║
-- ║  RLS habilitada (hereda patrón clients · G5).                     ║
-- ║  Aditiva: cero DROP de objetos · cero modificaciones destructivas.║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── aria_suggestions · NBA proactivo por cliente ────────────────────
CREATE TABLE IF NOT EXISTS aria_suggestions (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  user_id         uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  message         text NOT NULL,
  suggestion_type text NOT NULL CHECK (suggestion_type IN ('inactivity','upgrade_plan','profile_incomplete','no_addons')),
  is_read         boolean NOT NULL DEFAULT false,
  read_at         timestamptz,
  created_at      timestamptz NOT NULL DEFAULT now()
);

-- ─── Índice para listar no-leídas recientes por cliente ──────────────
CREATE INDEX IF NOT EXISTS idx_aria_suggestions_client_read
  ON aria_suggestions (client_id, is_read, created_at DESC);

-- ─── RLS ─────────────────────────────────────────────────────────────
ALTER TABLE aria_suggestions ENABLE ROW LEVEL SECURITY;

-- Least-privilege: el usuario solo LEE (SELECT) las sugerencias de sus clientes ·
-- toda la escritura (generar + marcar leídas) la hace el backend con service_role.
DROP POLICY IF EXISTS "aria_suggestions inherits clients RLS" ON aria_suggestions;
CREATE POLICY "aria_suggestions inherits clients RLS"
  ON aria_suggestions FOR SELECT
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

DROP POLICY IF EXISTS "Service role manages aria_suggestions" ON aria_suggestions;
CREATE POLICY "Service role manages aria_suggestions"
  ON aria_suggestions FOR ALL
  USING (auth.role() = 'service_role');

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SELECT manual en SQL Editor):
--   SELECT table_name FROM information_schema.tables
--     WHERE table_schema = 'public'
--     AND table_name = 'aria_suggestions';
--   -- Esperado: 1 fila
--
--   SELECT indexname FROM pg_indexes
--     WHERE tablename = 'aria_suggestions';
--   -- Esperado: aria_suggestions_pkey · idx_aria_suggestions_client_read
--
--   SELECT count(*) FROM aria_suggestions;
--   -- Esperado: 0 (tabla vacía tras migración)
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00028
-- ═══════════════════════════════════════════════════════════════════
