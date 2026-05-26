-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00027 · analytics_snapshots                           ║
-- ║  26 may 2026 · Centro de Inteligencia Fase 1                     ║
-- ║                                                                   ║
-- ║  Propósito: caché 24 h de resultados de análisis                  ║
-- ║   web-analysis · geo-check · aeo-check                           ║
-- ║                                                                   ║
-- ║  RLS habilitada (hereda patrón clients · G5).                     ║
-- ║  Aditiva: cero DROP · cero modificaciones destructivas.           ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── analytics_snapshots · caché Centro de Inteligencia ──────────────
CREATE TABLE IF NOT EXISTS analytics_snapshots (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  snapshot_type text NOT NULL CHECK (snapshot_type IN ('web_analysis','geo_check','aeo_check')),
  payload       jsonb NOT NULL DEFAULT '{}'::jsonb,
  score         integer CHECK (score IS NULL OR (score >= 0 AND score <= 100)),
  created_at    timestamptz NOT NULL DEFAULT now()
);

-- ─── Índice de lookup caché (más reciente por client + type) ─────────
CREATE INDEX IF NOT EXISTS idx_analytics_snapshots_lookup
  ON analytics_snapshots(client_id, snapshot_type, created_at DESC);

-- ─── RLS ─────────────────────────────────────────────────────────────
ALTER TABLE analytics_snapshots ENABLE ROW LEVEL SECURITY;

-- Least-privilege: el usuario solo LEE (SELECT) los snapshots de sus clientes ·
-- toda la escritura la hace el backend con service_role (la tabla es caché backend-mediada).
DROP POLICY IF EXISTS "analytics_snapshots inherits clients RLS" ON analytics_snapshots;
CREATE POLICY "analytics_snapshots inherits clients RLS"
  ON analytics_snapshots FOR SELECT
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

DROP POLICY IF EXISTS "Service role manages analytics_snapshots" ON analytics_snapshots;
CREATE POLICY "Service role manages analytics_snapshots"
  ON analytics_snapshots FOR ALL
  USING (auth.role() = 'service_role');

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SELECT manual en SQL Editor):
--   SELECT table_name FROM information_schema.tables
--     WHERE table_schema = 'public'
--     AND table_name = 'analytics_snapshots';
--   -- Esperado: 1 fila
--
--   SELECT indexname FROM pg_indexes
--     WHERE tablename = 'analytics_snapshots';
--   -- Esperado: analytics_snapshots_pkey · idx_analytics_snapshots_lookup
--
--   SELECT count(*) FROM analytics_snapshots;
--   -- Esperado: 0 (tabla vacía tras migración)
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00027
-- ═══════════════════════════════════════════════════════════════════
