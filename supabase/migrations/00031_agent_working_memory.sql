-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00031 · agent_working_memory                          ║
-- ║  26 may 2026 · DEBT-077 Caso A2 · memoria de trabajo de NOVA      ║
-- ║                                                                   ║
-- ║  Propósito: memoria de trabajo / handoff de los 44 agentes        ║
-- ║   (conversation · handoff · handoff_completion · brief_generated  ║
-- ║    · operational_rule · y tipos libres save_memory).             ║
-- ║                                                                   ║
-- ║  SEPARADA de agent_memory (memoria de decisiones del training     ║
-- ║   loop). El código backend escribe/lee a la tabla cuyo nombre se  ║
-- ║   swappea (omega_agent_memory → agent_working_memory) SIN cambiar  ║
-- ║   columnas: esta tabla calza 1:1 con el código.                  ║
-- ║                                                                   ║
-- ║  Tabla interna · solo backend (service_role) escribe/lee.         ║
-- ║  Aditiva: cero DROP de tablas · NO toca agent_memory.            ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── agent_working_memory · memoria de trabajo / handoff de agentes ──
CREATE TABLE IF NOT EXISTS agent_working_memory (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_code      text NOT NULL,
  memory_type     text NOT NULL,
  -- content es jsonb: el código escribe tanto objetos (conversation/handoff/
  -- brief_generated) como strings JSON (operational_rule en save_nova_memory).
  -- Se consulta content->>task_id en el filtro de handoffs.
  content         jsonb NOT NULL,
  related_agents  jsonb,
  -- priority es text (sin CHECK): el código mezcla casings/sets —
  -- handoff usa 'URGENT'|'HIGH'|'NORMAL'|'LOW' · save_memory usa 'high'|'medium'|'low'.
  priority        text,
  session_id      text,
  client_id       uuid REFERENCES clients(id) ON DELETE SET NULL,
  expires_at      timestamptz,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

-- ─── Índices ─────────────────────────────────────────────────────────
-- Filtro principal por agente (get_agent_context · get_pending_handoffs · briefing)
CREATE INDEX IF NOT EXISTS idx_agent_working_memory_agent
  ON agent_working_memory (agent_code);

-- Orden por recencia (get_briefing ordena created_at DESC)
CREATE INDEX IF NOT EXISTS idx_agent_working_memory_created
  ON agent_working_memory (created_at DESC);

-- GIN sobre content para el lookup de handoffs por task_id (content->>task_id)
CREATE INDEX IF NOT EXISTS idx_agent_working_memory_content_gin
  ON agent_working_memory USING gin (content);

-- ─── RLS ─────────────────────────────────────────────────────────────
ALTER TABLE agent_working_memory ENABLE ROW LEVEL SECURITY;

-- Tabla interna: solo el backend (service_role) escribe y lee ·
-- sin acceso de cliente.
DROP POLICY IF EXISTS "Service role manages agent_working_memory" ON agent_working_memory;
CREATE POLICY "Service role manages agent_working_memory"
  ON agent_working_memory FOR ALL
  USING (auth.role() = 'service_role');

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SELECT manual en SQL Editor):
--   SELECT table_name FROM information_schema.tables
--     WHERE table_schema = 'public'
--     AND table_name = 'agent_working_memory';
--   -- Esperado: 1 fila
--
--   SELECT indexname FROM pg_indexes
--     WHERE tablename = 'agent_working_memory';
--   -- Esperado: agent_working_memory_pkey · idx_agent_working_memory_agent
--   --           · idx_agent_working_memory_created · idx_agent_working_memory_content_gin
--
--   SELECT count(*) FROM agent_working_memory;
--   -- Esperado: 0 (tabla vacía tras migración)
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00031
-- ═══════════════════════════════════════════════════════════════════
