-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00043 · strategies                                     ║
-- ║  30 may 2026 · DEBT-096 Fase 1 · Página Estrategias               ║
-- ║                                                                   ║
-- ║  ARIA genera estrategias (on-demand en Fase 1 · cron en Fase 2)   ║
-- ║  reusando el pipeline de contexto de ARIA. 1 fila/estrategia.     ║
-- ║  RLS client-scoped (cliente ve las suyas · reseller las de sus    ║
-- ║  clientes) · service_role escribe (generación/archivado backend). ║
-- ║  Sin tocar limits_omega (cadencia en spec · SHA1 intacto).        ║
-- ╚═══════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS strategies (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  titulo          text NOT NULL,
  tipo            text NOT NULL DEFAULT 'manual'
                    CHECK (tipo IN ('semanal', 'tres_semana', 'diaria', 'manual')),
  contenido       jsonb NOT NULL DEFAULT '{}'::jsonb,   -- secciones + posts sugeridos
  estado          text NOT NULL DEFAULT 'active'
                    CHECK (estado IN ('active', 'used', 'archived')),
  created_by_aria boolean NOT NULL DEFAULT true,
  used_at         timestamptz,
  archived_at     timestamptz,
  created_at      timestamptz NOT NULL DEFAULT now()
);

-- Filtro de la página: activas (vista principal) vs archivadas (historial).
CREATE INDEX IF NOT EXISTS idx_strategies_client_estado ON strategies (client_id, estado);
-- (idempotente · igual que CREATE TABLE IF NOT EXISTS · un reintento no falla a medias)

ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;

-- Cliente ve solo sus estrategias · reseller las de sus clientes (patrón 00034).
DROP POLICY IF EXISTS "strategies client read" ON strategies;
CREATE POLICY "strategies client read"
  ON strategies FOR SELECT
  USING (
    client_id IN (
      SELECT id FROM clients
      WHERE user_id = auth.uid()
         OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
    )
  );

-- service_role gestiona (generación on-demand, archivar, marcar usada).
DROP POLICY IF EXISTS "strategies service_role all" ON strategies;
CREATE POLICY "strategies service_role all"
  ON strategies FOR ALL
  USING (auth.role() = 'service_role');
