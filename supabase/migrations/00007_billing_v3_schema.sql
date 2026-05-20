-- ═══════════════════════════════════════════════════════════════════
-- OmegaRaisen — Migración 00007: Billing V3 schema (bc_billing)
-- · stripe_customer_id en clients (mapping Stripe customer → cliente OMEGA)
-- · webhook_events para idempotencia X4 (UNIQUE event_id)
-- · RLS service_role only · solo backend webhook handler escribe
-- ═══════════════════════════════════════════════════════════════════

-- ─── 1. stripe_customer_id en clients ─────────────────────────────
ALTER TABLE clients
  ADD COLUMN IF NOT EXISTS stripe_customer_id text;

-- Partial unique: solo aplica si stripe_customer_id NOT NULL.
-- Filas pre-billing sin customer ID conviven sin romper · idempotencia
-- de re-aplicación garantizada.
CREATE UNIQUE INDEX IF NOT EXISTS uq_clients_stripe_customer_id
  ON clients (stripe_customer_id)
  WHERE stripe_customer_id IS NOT NULL;

-- ─── 2. Tabla webhook_events · idempotencia X4 ────────────────────
CREATE TABLE IF NOT EXISTS webhook_events (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  provider     text NOT NULL CHECK (provider IN ('stripe')),
  event_id     text UNIQUE NOT NULL,    -- evt_XXX · UNIQUE = guard idempotencia
  event_type   text NOT NULL,           -- customer.subscription.{created,updated,deleted}, checkout.session.completed
  payload      jsonb NOT NULL,          -- raw forensics (decisión #3 · no billing_audit user-facing por ahora)
  processed_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_webhook_events_provider_type
  ON webhook_events (provider, event_type);

CREATE INDEX IF NOT EXISTS idx_webhook_events_processed_at
  ON webhook_events (processed_at DESC);

ALTER TABLE webhook_events ENABLE ROW LEVEL SECURITY;

-- service_role only · frontend nunca lee/escribe webhook_events
-- (audit forensics privado · solo backend webhook handler)
CREATE POLICY "webhook_events service role only"
  ON webhook_events FOR ALL
  USING (auth.role() = 'service_role');
