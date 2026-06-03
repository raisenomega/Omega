-- 00054_sentinel_runtime.sql
-- SENTINEL Capa 9 · observabilidad runtime. 3 tablas + RLS service_role. Aditiva.
-- backend_error_log (5xx+exceptions vía middleware) · frontend_error_log (window.onerror/ErrorBoundary)
-- · sentinel_runtime_scans (corrida cada 5min).

CREATE TABLE IF NOT EXISTS backend_error_log (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  request_path  text,
  http_method   text,
  status_code   int,
  error_class   text,
  error_message text,
  stack_trace   text,
  user_id       uuid,
  ip_address    text,
  user_agent    text,
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_backend_error_log_created ON backend_error_log (created_at DESC, status_code);
CREATE INDEX IF NOT EXISTS idx_backend_error_log_class   ON backend_error_log (error_class);

CREATE TABLE IF NOT EXISTS frontend_error_log (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  message    text,
  stack      text,
  url        text,
  signature  text NOT NULL,
  user_id    uuid,
  user_agent text,
  ip_address text,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_frontend_error_log_created ON frontend_error_log (created_at DESC, signature);
CREATE INDEX IF NOT EXISTS idx_frontend_error_log_sig     ON frontend_error_log (signature);

CREATE TABLE IF NOT EXISTS sentinel_runtime_scans (
  id                     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scanned_at             timestamptz,
  window_minutes         int NOT NULL DEFAULT 5,
  backend_error_rate_pct numeric,
  backend_exception_count int NOT NULL DEFAULT 0,
  frontend_error_count   int NOT NULL DEFAULT 0,
  recurring_patterns     jsonb NOT NULL DEFAULT '[]'::jsonb,
  railway_5xx_count      int,
  score                  int NOT NULL DEFAULT 100,
  issues                 jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at             timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sentinel_runtime_scans_created ON sentinel_runtime_scans (created_at DESC);

ALTER TABLE backend_error_log      ENABLE ROW LEVEL SECURITY;
ALTER TABLE frontend_error_log     ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentinel_runtime_scans ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "backend_error_log_service_role_all" ON backend_error_log;
CREATE POLICY "backend_error_log_service_role_all" ON backend_error_log FOR ALL TO service_role USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "frontend_error_log_service_role_all" ON frontend_error_log;
CREATE POLICY "frontend_error_log_service_role_all" ON frontend_error_log FOR ALL TO service_role USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "sentinel_runtime_scans_service_role_all" ON sentinel_runtime_scans;
CREATE POLICY "sentinel_runtime_scans_service_role_all" ON sentinel_runtime_scans FOR ALL TO service_role USING (true) WITH CHECK (true);
