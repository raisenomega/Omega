-- 00055_sentinel_performance.sql
-- SENTINEL Capa 10 · performance/APM. 3 tablas + 2 funciones. RLS service_role. Aditiva.
-- request_timing_log (1 fila/request · cierra el error_rate de Capa 9) · frontend_build_stats
-- (GH Action) · sentinel_performance_scans (corrida 5min).

CREATE TABLE IF NOT EXISTS request_timing_log (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  path        text NOT NULL,
  method      text NOT NULL,
  status_code int NOT NULL,
  duration_ms int NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_request_timing_created      ON request_timing_log (created_at DESC, path);
CREATE INDEX IF NOT EXISTS idx_request_timing_path         ON request_timing_log (path, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_request_timing_status       ON request_timing_log (status_code, created_at DESC);

CREATE TABLE IF NOT EXISTS frontend_build_stats (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  git_sha         text NOT NULL,
  bundle_size_kb  int NOT NULL,
  main_chunk_kb   int,
  vendor_chunk_kb int,
  total_chunks    int,
  build_duration_s numeric,
  github_run_id   text,
  created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_frontend_build_stats_created ON frontend_build_stats (created_at DESC);

CREATE TABLE IF NOT EXISTS sentinel_performance_scans (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scanned_at        timestamptz,
  window_minutes    int NOT NULL DEFAULT 5,
  p95_per_endpoint  jsonb NOT NULL DEFAULT '[]'::jsonb,
  p99_per_endpoint  jsonb NOT NULL DEFAULT '[]'::jsonb,
  slow_queries      jsonb NOT NULL DEFAULT '[]'::jsonb,
  bundle_size_kb    int,
  memory_pct        numeric,
  cpu_pct           numeric,
  score             int NOT NULL DEFAULT 100,
  issues            jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at        timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sentinel_performance_scans_created ON sentinel_performance_scans (created_at DESC);

ALTER TABLE request_timing_log         ENABLE ROW LEVEL SECURITY;
ALTER TABLE frontend_build_stats       ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentinel_performance_scans ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "request_timing_log_service_role_all" ON request_timing_log;
CREATE POLICY "request_timing_log_service_role_all" ON request_timing_log FOR ALL TO service_role USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "frontend_build_stats_service_role_all" ON frontend_build_stats;
CREATE POLICY "frontend_build_stats_service_role_all" ON frontend_build_stats FOR ALL TO service_role USING (true) WITH CHECK (true);
DROP POLICY IF EXISTS "sentinel_performance_scans_service_role_all" ON sentinel_performance_scans;
CREATE POLICY "sentinel_performance_scans_service_role_all" ON sentinel_performance_scans FOR ALL TO service_role USING (true) WITH CHECK (true);

-- p95/p99 por endpoint en la ventana (HAVING count>=5 · top 10 por p95).
CREATE OR REPLACE FUNCTION public.sentinel_endpoint_latency(window_minutes int)
RETURNS jsonb LANGUAGE sql STABLE AS $$
  SELECT coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) FROM (
    SELECT path,
           count(*) AS calls,
           round(percentile_cont(0.95) WITHIN GROUP (ORDER BY duration_ms))::int AS p95,
           round(percentile_cont(0.99) WITHIN GROUP (ORDER BY duration_ms))::int AS p99,
           max(status_code) AS max_status
    FROM request_timing_log
    WHERE created_at > now() - (window_minutes || ' minutes')::interval
    GROUP BY path HAVING count(*) >= 5
    ORDER BY p95 DESC LIMIT 10
  ) t;
$$;
GRANT EXECUTE ON FUNCTION public.sentinel_endpoint_latency(int) TO service_role;

-- Slow queries de pg_stat_statements (si no está la extensión → []).
CREATE OR REPLACE FUNCTION public.sentinel_slow_queries(min_mean_ms int, limit_rows int)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_catalog AS $$
DECLARE v jsonb;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements') THEN
    RETURN '[]'::jsonb;
  END IF;
  SELECT coalesce(jsonb_agg(to_jsonb(t)), '[]'::jsonb) INTO v FROM (
    SELECT left(query, 200) AS query, calls, round(mean_exec_time::numeric, 1) AS mean_ms
    FROM pg_stat_statements WHERE mean_exec_time > min_mean_ms
    ORDER BY mean_exec_time DESC LIMIT limit_rows
  ) t;
  RETURN v;
END;
$$;
GRANT EXECUTE ON FUNCTION public.sentinel_slow_queries(int, int) TO service_role;
