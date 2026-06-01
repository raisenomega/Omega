-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00045 · mcp_health_log                                 ║
-- ║  1 jun 2026 · HERMES CORE fase 1 · salud de integraciones externas║
-- ║                                                                   ║
-- ║  Propósito: registro del cron HERMES Capa 1 (ping liviano cada    ║
-- ║   5 min). Por integración viva guarda el estado de salud:         ║
-- ║   'ok' (credencial presente) · 'no_configurado' (sin credencial). ║
-- ║   Estado 'last_use_failed' + columna last_use = fase 1.5          ║
-- ║   (DEBT-HERMES-USAGE-TRACKING · last_use nace NULL).              ║
-- ║                                                                   ║
-- ║  RLS habilitada · solo service_role (tabla interna de HERMES      ║
-- ║   · backend-only · sin acceso de cliente · hermana de             ║
-- ║   sentinel_risk_scores 00029).                                    ║
-- ║  Aditiva: cero DROP de tablas · cero modificaciones destructivas. ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── mcp_health_log · estado de salud por integración (HERMES Capa 1) ─
CREATE TABLE IF NOT EXISTS mcp_health_log (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  integration  text NOT NULL,                  -- 'anthropic'|'nano_banana'|'veo3'|'voyage'|'brave'|'stripe'|'resend' · SIN CHECK: el set crece (Zernio/Tavily/... futuras) · un CHECK forzaría ALTER por cada integración nueva
  status       text NOT NULL CHECK (status IN ('ok','no_configurado','last_use_failed')),  -- enum cerrado · 3 estados incluido el de fase 1.5 (evita micro-migración)
  detail       text,                           -- mensaje legible opcional
  last_use     timestamptz,                    -- NULL en fase 1 · poblado en fase 1.5 (DEBT-HERMES-USAGE-TRACKING)
  checked_at   timestamptz NOT NULL DEFAULT now(),
  created_at   timestamptz NOT NULL DEFAULT now()
);

-- Índice para "última corrida": estado más reciente global por checked_at DESC.
CREATE INDEX IF NOT EXISTS idx_mcp_health_log_checked_at
  ON mcp_health_log (checked_at DESC);

-- Índice para "último estado por integración": filtra por integration + DESC.
CREATE INDEX IF NOT EXISTS idx_mcp_health_log_integration
  ON mcp_health_log (integration, checked_at DESC);

-- ─── RLS · solo service_role (tabla interna backend-only · como 00029) ─
ALTER TABLE mcp_health_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Service role manages mcp_health_log" ON mcp_health_log;
CREATE POLICY "Service role manages mcp_health_log"
  ON mcp_health_log FOR ALL
  USING (auth.role() = 'service_role');

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SELECT manual en SQL Editor):
--   SELECT table_name FROM information_schema.tables
--     WHERE table_schema = 'public' AND table_name = 'mcp_health_log';
--   -- Esperado: 1 fila
--
--   SELECT indexname FROM pg_indexes WHERE tablename = 'mcp_health_log';
--   -- Esperado: pkey + idx_mcp_health_log_checked_at + idx_mcp_health_log_integration
--
--   SELECT count(*) FROM mcp_health_log;
--   -- Esperado: 0 (tabla vacía tras migración · se puebla con el 1er cron)
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00045
-- ═══════════════════════════════════════════════════════════════════
