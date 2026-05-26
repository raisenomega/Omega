-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00032 · agent_executions                              ║
-- ║  26 may 2026 · DEBT-049 · tabla inexistente (consumidores 500)    ║
-- ║                                                                   ║
-- ║  Propósito: registrar las corridas individuales de los agentes    ║
-- ║   (input/output · status · timing). Calza 1:1 con la entidad      ║
-- ║   AgentExecution (domain/agents/entities.py) y con lo que          ║
-- ║   agent_repository.py escribe (create/update_execution) y los      ║
-- ║   consumidores leen (get_executions · omega/get_activity ·        ║
-- ║   omega·analytics/get_dashboard) [DEBT-052/053].                  ║
-- ║                                                                   ║
-- ║  RLS habilitada · SELECT client-scoped (cliente ve su actividad,  ║
-- ║   DEBT-053) + service_role FOR ALL (backend write + superadmin).  ║
-- ║  Aditiva: solo CREATE · cero DROP de tablas existentes.           ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── agent_executions · corridas individuales de agentes ─────────────
CREATE TABLE IF NOT EXISTS agent_executions (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id          text NOT NULL,                               -- código del agente (espejo de AgentExecution.agent_id)
  client_id         uuid REFERENCES clients(id) ON DELETE CASCADE,
  user_id           uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  triggered_by      text NOT NULL DEFAULT 'manual',
  input_data        jsonb NOT NULL DEFAULT '{}'::jsonb,
  output_data       jsonb NOT NULL DEFAULT '{}'::jsonb,
  error_message     text,
  status            text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','completed','failed','cancelled')),
  started_at        timestamptz,
  completed_at      timestamptz,
  execution_time_ms integer,
  metadata          jsonb NOT NULL DEFAULT '{}'::jsonb,
  is_active         boolean NOT NULL DEFAULT true,
  created_at        timestamptz NOT NULL DEFAULT now()
);

-- ─── Índices ─────────────────────────────────────────────────────────
-- Filtro principal por agente (find_executions_by_agent · count_executions)
CREATE INDEX IF NOT EXISTS idx_agent_executions_agent
  ON agent_executions (agent_id);

-- Actividad del cliente más reciente (DEBT-052/053 · SELECT client-scoped)
CREATE INDEX IF NOT EXISTS idx_agent_executions_client_created
  ON agent_executions (client_id, created_at DESC);

-- Filtro por estado (count_executions · success_rate del dashboard)
CREATE INDEX IF NOT EXISTS idx_agent_executions_status
  ON agent_executions (status);

-- Orden por recencia de corrida (get_activity · get_dashboard ordenan started_at DESC)
CREATE INDEX IF NOT EXISTS idx_agent_executions_started
  ON agent_executions (started_at DESC);

-- ─── RLS ─────────────────────────────────────────────────────────────
ALTER TABLE agent_executions ENABLE ROW LEVEL SECURITY;

-- El cliente LEE (SELECT) las corridas de sus propios clientes (DEBT-053:
-- el cliente ve su actividad). Mismo patrón que 00027/00028 (hereda clients · G5).
DROP POLICY IF EXISTS "agent_executions inherits clients RLS" ON agent_executions;
CREATE POLICY "agent_executions inherits clients RLS"
  ON agent_executions FOR SELECT
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

-- Toda la escritura (create/update_execution) la hace el backend con
-- service_role · y las lecturas superadmin (omega/*) que no son client-scoped.
DROP POLICY IF EXISTS "Service role manages agent_executions" ON agent_executions;
CREATE POLICY "Service role manages agent_executions"
  ON agent_executions FOR ALL
  USING (auth.role() = 'service_role');

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SELECT manual en SQL Editor):
--   SELECT table_name FROM information_schema.tables
--     WHERE table_schema = 'public'
--     AND table_name = 'agent_executions';
--   -- Esperado: 1 fila
--
--   SELECT indexname FROM pg_indexes
--     WHERE tablename = 'agent_executions';
--   -- Esperado: agent_executions_pkey · idx_agent_executions_agent
--   --           · idx_agent_executions_client_created · idx_agent_executions_status
--   --           · idx_agent_executions_started
--
--   SELECT count(*) FROM agent_executions;
--   -- Esperado: 0 (tabla vacía tras migración)
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00032
-- ═══════════════════════════════════════════════════════════════════
