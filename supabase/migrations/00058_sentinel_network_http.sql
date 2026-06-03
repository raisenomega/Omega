-- 00058_sentinel_network_http.sql
-- SENTINEL Sprint 2 · Capa 3 (Red y HTTP) · 11º componente.
-- Una fila por target por scan (frontend www + backend Railway). Worker cada 2h.
-- RLS solo service_role (replica patrón sentinel_scans). Aditiva · CREATE IF NOT EXISTS.

CREATE TABLE IF NOT EXISTS sentinel_network_http_scans (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scanned_at        timestamptz NOT NULL DEFAULT now(),
  target_url        text NOT NULL,
  headers_check     jsonb NOT NULL DEFAULT '{}'::jsonb,   -- {final_url, present:{}, missing:[]}
  tls_check         jsonb NOT NULL DEFAULT '{}'::jsonb,   -- {version, cert_subject, cert_issuer, cert_expires_at, days_until_expiry}
  rate_limit_check  jsonb,                                -- {active, limit_per_minute, scope, exempt_prefixes, verified_by} · null en frontend
  cors_check        jsonb,                                -- {evil_origin_acao, wildcard_detected, reflects_untrusted} · null en frontend
  score             integer NOT NULL DEFAULT 100,
  issues            jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at        timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sentinel_network_http_created_at
  ON sentinel_network_http_scans (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sentinel_network_http_target
  ON sentinel_network_http_scans (target_url, created_at DESC);

ALTER TABLE sentinel_network_http_scans ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "sentinel_network_http_service_role_all" ON sentinel_network_http_scans;
CREATE POLICY "sentinel_network_http_service_role_all"
  ON sentinel_network_http_scans
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply:  SELECT count(*) FROM sentinel_network_http_scans;  -- esperado 0
-- ═══════════════════════════════════════════════════════════════════
