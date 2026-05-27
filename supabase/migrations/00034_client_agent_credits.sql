-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00034 · client_agent_credits + client_credit_ledger    ║
-- ║  26 may 2026 · DEBT-052 · sistema de créditos prepagados por agente║
-- ║                                                                   ║
-- ║  Capa NUEVA por encima del techo inmutable limits_omega           ║
-- ║   MAX_USD_DIARIO_API_POR_CLIENTE ($5/día · circuit-breaker). NO    ║
-- ║   modifica el guardrail (decisión owner · SHA1 intacto · I1/G1).  ║
-- ║                                                                   ║
-- ║  client_agent_credits: 1 fila/cliente · budget mensual prepagado  ║
-- ║   + consumido + periodo + packs verticales activos.               ║
-- ║  client_credit_ledger: 1 fila/débito · desglose por agente para   ║
-- ║   el AI Tab (consumo por agente · FASE 5).                        ║
-- ║                                                                   ║
-- ║  RLS: cliente LEE lo suyo (saldo) · service_role FOR ALL (débito  ║
-- ║   + admin superadmin). Aditiva: solo CREATE · cero DROP.          ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── client_agent_credits · budget prepagado por cliente ─────────────
CREATE TABLE IF NOT EXISTS client_agent_credits (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id           uuid NOT NULL UNIQUE REFERENCES clients(id) ON DELETE CASCADE,
  budget_usd_mensual  numeric(10,2) NOT NULL DEFAULT 0,      -- prepago del periodo (USD)
  consumido_usd       numeric(12,6) NOT NULL DEFAULT 0,      -- acumula micro-costos (precisión)
  periodo_start       timestamptz NOT NULL DEFAULT now(),
  periodo_end         timestamptz NOT NULL,
  packs               jsonb NOT NULL DEFAULT '[]'::jsonb,    -- verticales activos: creativo|estratega|guardian
  created_at          timestamptz NOT NULL DEFAULT now(),
  updated_at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_client_agent_credits_client
  ON client_agent_credits (client_id);

ALTER TABLE client_agent_credits ENABLE ROW LEVEL SECURITY;

-- Cliente LEE su propio saldo (mismo patrón client-scoped que 00032/00028 · G5)
DROP POLICY IF EXISTS "client_agent_credits inherits clients RLS" ON client_agent_credits;
CREATE POLICY "client_agent_credits inherits clients RLS"
  ON client_agent_credits FOR SELECT
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

-- Toda escritura (débito de créditos · admin superadmin mover/liberar) = service_role.
DROP POLICY IF EXISTS "Service role manages client_agent_credits" ON client_agent_credits;
CREATE POLICY "Service role manages client_agent_credits"
  ON client_agent_credits FOR ALL
  USING (auth.role() = 'service_role');

-- ─── client_credit_ledger · 1 fila por débito (desglose por agente) ──
CREATE TABLE IF NOT EXISTS client_credit_ledger (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  agent_code    text NOT NULL,                              -- código del agente que consumió
  cost_usd      numeric(12,6) NOT NULL,                     -- costo real del débito
  model         text,                                       -- modelo/motor usado (tracking)
  execution_id  uuid,                                       -- link opcional a agent_executions
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_client_credit_ledger_client_created
  ON client_credit_ledger (client_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_client_credit_ledger_agent
  ON client_credit_ledger (client_id, agent_code);

ALTER TABLE client_credit_ledger ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "client_credit_ledger inherits clients RLS" ON client_credit_ledger;
CREATE POLICY "client_credit_ledger inherits clients RLS"
  ON client_credit_ledger FOR SELECT
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

DROP POLICY IF EXISTS "Service role manages client_credit_ledger" ON client_credit_ledger;
CREATE POLICY "Service role manages client_credit_ledger"
  ON client_credit_ledger FOR ALL
  USING (auth.role() = 'service_role');

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SQL Editor):
--   SELECT table_name FROM information_schema.tables
--     WHERE table_schema='public'
--     AND table_name IN ('client_agent_credits','client_credit_ledger');
--   -- Esperado: 2 filas
--
--   SELECT tablename, policyname FROM pg_policies
--     WHERE tablename IN ('client_agent_credits','client_credit_ledger');
--   -- Esperado: 2 políticas por tabla (SELECT client-scoped + service_role FOR ALL)
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00034
-- ═══════════════════════════════════════════════════════════════════
