-- 00059_sentinel_integrations.sql
-- SENTINEL Sprint 2 · Capa 11 (Integraciones externas) · 12º componente.
-- Una fila por scan (worker hourly). Monitorea Stripe webhooks/Connect + OAuth (social_accounts).
-- Incluye función RPC para el check estructural X4 (idempotencia Stripe = event_id UNIQUE).
-- RLS service_role. Aditiva · CREATE IF NOT EXISTS.

CREATE TABLE IF NOT EXISTS sentinel_integrations_scans (
  id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scanned_at            timestamptz NOT NULL DEFAULT now(),
  stripe_webhooks_check jsonb NOT NULL DEFAULT '{}'::jsonb,  -- {event_count_24h, idempotency_enforced, stripe_liveness}
  stripe_connect_check  jsonb NOT NULL DEFAULT '{}'::jsonb,  -- {total_resellers, with_stripe_account, note}
  oauth_check           jsonb NOT NULL DEFAULT '{}'::jsonb,  -- {per_platform:[], total, connected, expiring_24h, expiring_7d}
  mcp_check             jsonb,                                -- {covered_by:"HERMES Capa 1", ...}
  score                 integer NOT NULL DEFAULT 100,
  issues                jsonb NOT NULL DEFAULT '[]'::jsonb,
  coverage_note         text,
  created_at            timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sentinel_integrations_created_at
  ON sentinel_integrations_scans (created_at DESC);

ALTER TABLE sentinel_integrations_scans ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "sentinel_integrations_service_role_all" ON sentinel_integrations_scans;
CREATE POLICY "sentinel_integrations_service_role_all"
  ON sentinel_integrations_scans
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- X4 (DDD_REGLAS) · verificación estructural en vivo: ¿webhook_events.event_id tiene UNIQUE?
-- STABLE + SECURITY DEFINER para leer information_schema desde el worker (service_role).
CREATE OR REPLACE FUNCTION sentinel_webhook_idempotency_enforced()
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$
  SELECT EXISTS (
    SELECT 1
    FROM information_schema.constraint_column_usage ccu
    JOIN information_schema.table_constraints tc ON tc.constraint_name = ccu.constraint_name
    WHERE ccu.table_name = 'webhook_events'
      AND ccu.column_name = 'event_id'
      AND tc.constraint_type = 'UNIQUE'
  );
$$;

GRANT EXECUTE ON FUNCTION sentinel_webhook_idempotency_enforced() TO service_role;

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply:  SELECT sentinel_webhook_idempotency_enforced();  -- esperado true
-- ═══════════════════════════════════════════════════════════════════
