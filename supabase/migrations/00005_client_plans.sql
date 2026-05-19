-- ═══════════════════════════════════════════════════════════════════
-- OmegaRaisen — Migración 00005: client_plans (billing cycle source)
-- · Step 3 §7 dashboard: source para "Renueva en N días" + period boundary
-- · Default cycle = 30d desde created_at (sin Stripe activo aún · DEBT-032)
-- · Cuando Stripe se enchufe (Fase 3 §3.x), webhook actualiza current_period_end
-- ═══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS client_plans (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id              uuid NOT NULL UNIQUE REFERENCES clients(id) ON DELETE CASCADE,
  plan                   text NOT NULL CHECK (plan IN ('adopcion','basic','pro','enterprise')),
  current_period_start   timestamptz NOT NULL DEFAULT now(),
  current_period_end     timestamptz NOT NULL,
  stripe_subscription_id text,
  addons                 jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at             timestamptz NOT NULL DEFAULT now(),
  updated_at             timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_client_plans_period_end ON client_plans (current_period_end);
CREATE INDEX IF NOT EXISTS idx_client_plans_plan       ON client_plans (plan);

ALTER TABLE client_plans ENABLE ROW LEVEL SECURITY;

-- service_role: full
CREATE POLICY "client_plans service role full"
  ON client_plans FOR ALL
  USING (auth.role() = 'service_role');

-- Cliente final dueño (clients.user_id = auth.uid): SELECT su plan
-- Reseller dueño del cliente: SELECT también
-- Patrón (SELECT auth.uid()) para evitar Auth RLS Init Plan lint
CREATE POLICY "client_plans owner view"
  ON client_plans FOR SELECT
  USING (
    client_id IN (
      SELECT id FROM clients
      WHERE user_id = (SELECT auth.uid())
         OR reseller_id IN (
           SELECT id FROM resellers WHERE owner_user_id = (SELECT auth.uid())
         )
    )
  );

-- Reseller dueño: ALL (UPDATE manual de plan/addons hasta que Stripe webhook lo haga)
CREATE POLICY "client_plans reseller manage"
  ON client_plans FOR ALL
  USING (
    client_id IN (
      SELECT id FROM clients
      WHERE reseller_id IN (
        SELECT id FROM resellers WHERE owner_user_id = (SELECT auth.uid())
      )
    )
  );

-- ─── Backfill: clients existentes obtienen período = created_at..created_at+30d
-- ON CONFLICT (client_id) DO NOTHING para idempotencia (re-aplicación segura)
-- CASE para tolerar valores legacy de clients.plan que no matchean CHECK
INSERT INTO client_plans (client_id, plan, current_period_start, current_period_end)
SELECT id,
       CASE
         WHEN plan IN ('adopcion','basic','pro','enterprise') THEN plan
         ELSE 'basic'
       END,
       created_at,
       created_at + interval '30 days'
FROM clients
ON CONFLICT (client_id) DO NOTHING;
