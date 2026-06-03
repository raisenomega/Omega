-- 00052_sentinel_rls_audit.sql
-- SENTINEL Capa 6 · auditoría RLS automática (función SECURITY DEFINER + tabla de corridas).
-- La función lee pg_policies/pg_class (catálogos) → SECURITY DEFINER (owner=postgres) para
-- que service_role pueda invocarla vía rpc. Excluye tablas internas (sentinel_/hermes_/omega_audit).

-- ─── Función de auditoría ────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.sentinel_rls_audit()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_catalog
AS $$
DECLARE
  v_issues jsonb := '[]'::jsonb;
  v_tmp jsonb;
  v_total int;
BEGIN
  SELECT count(*) INTO v_total FROM pg_tables WHERE schemaname = 'public';

  -- CHECK 1 · CRITICAL · tabla pública sin RLS habilitado
  SELECT coalesce(jsonb_agg(jsonb_build_object(
           'table', c.relname, 'issue_type', 'NO_RLS', 'severity', 'CRITICAL',
           'detail', 'Tabla pública sin RLS habilitado')), '[]'::jsonb)
  INTO v_tmp
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = 'public'
  WHERE c.relkind = 'r' AND NOT c.relrowsecurity
    AND c.relname NOT LIKE 'sentinel_%' AND c.relname NOT LIKE 'hermes_%' AND c.relname <> 'omega_audit_log';
  v_issues := v_issues || v_tmp;

  -- CHECK 2 · HIGH · RLS habilitado pero 0 policies (deny-all silencioso)
  SELECT coalesce(jsonb_agg(jsonb_build_object(
           'table', c.relname, 'issue_type', 'RLS_NO_POLICIES', 'severity', 'HIGH',
           'detail', 'RLS habilitado pero sin policies (deny-all silencioso)')), '[]'::jsonb)
  INTO v_tmp
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = 'public'
  WHERE c.relkind = 'r' AND c.relrowsecurity
    AND c.relname NOT LIKE 'sentinel_%' AND c.relname NOT LIKE 'hermes_%' AND c.relname <> 'omega_audit_log'
    AND NOT EXISTS (SELECT 1 FROM pg_policies p WHERE p.schemaname = 'public' AND p.tablename = c.relname);
  v_issues := v_issues || v_tmp;

  -- CHECK 3 · HIGH · policy USING(true) que toca authenticated/anon/public (excluye service_role-only)
  SELECT coalesce(jsonb_agg(jsonb_build_object(
           'table', p.tablename, 'issue_type', 'PERMISSIVE_TRUE', 'severity', 'HIGH',
           'detail', 'Policy ' || p.policyname || ' con USING(true) sobre roles no-service')), '[]'::jsonb)
  INTO v_tmp
  FROM pg_policies p
  WHERE p.schemaname = 'public' AND p.qual = 'true'
    AND array_to_string(p.roles, ',') <> 'service_role'
    AND p.tablename NOT LIKE 'sentinel_%' AND p.tablename NOT LIKE 'hermes_%' AND p.tablename <> 'omega_audit_log';
  v_issues := v_issues || v_tmp;

  -- CHECK 4 · MEDIUM · tiene policy SELECT pero ninguna de escritura (INSERT/UPDATE/DELETE/ALL)
  SELECT coalesce(jsonb_agg(jsonb_build_object(
           'table', t.tablename, 'issue_type', 'ASYMMETRIC_POLICIES', 'severity', 'MEDIUM',
           'detail', 'Tiene policy SELECT pero ninguna INSERT/UPDATE/DELETE')), '[]'::jsonb)
  INTO v_tmp
  FROM (
    SELECT DISTINCT p.tablename FROM pg_policies p
    WHERE p.schemaname = 'public' AND p.cmd = 'SELECT'
      AND p.tablename NOT LIKE 'sentinel_%' AND p.tablename NOT LIKE 'hermes_%' AND p.tablename <> 'omega_audit_log'
  ) t
  WHERE NOT EXISTS (
    SELECT 1 FROM pg_policies p2 WHERE p2.schemaname = 'public' AND p2.tablename = t.tablename
      AND p2.cmd IN ('INSERT', 'UPDATE', 'DELETE', 'ALL'));
  v_issues := v_issues || v_tmp;

  -- CHECK 5 · MEDIUM · policy too-broad (solo auth.uid() IS NOT NULL · sin client_id/user_id)
  SELECT coalesce(jsonb_agg(jsonb_build_object(
           'table', p.tablename, 'issue_type', 'TOO_BROAD', 'severity', 'MEDIUM',
           'detail', 'Policy ' || p.policyname || ' solo chequea auth.uid() IS NOT NULL (sin scope)')), '[]'::jsonb)
  INTO v_tmp
  FROM pg_policies p
  WHERE p.schemaname = 'public'
    AND p.qual ILIKE '%auth.uid() IS NOT NULL%'
    AND p.qual NOT ILIKE '%client_id%' AND p.qual NOT ILIKE '%user_id%'
    AND p.tablename NOT LIKE 'sentinel_%' AND p.tablename NOT LIKE 'hermes_%' AND p.tablename <> 'omega_audit_log';
  v_issues := v_issues || v_tmp;

  RETURN jsonb_build_object(
    'scanned_at', now(),
    'total_tables', v_total,
    'total_issues', jsonb_array_length(v_issues),
    'by_severity', jsonb_build_object(
      'critical', (SELECT count(*) FROM jsonb_array_elements(v_issues) e WHERE e->>'severity' = 'CRITICAL'),
      'high',     (SELECT count(*) FROM jsonb_array_elements(v_issues) e WHERE e->>'severity' = 'HIGH'),
      'medium',   (SELECT count(*) FROM jsonb_array_elements(v_issues) e WHERE e->>'severity' = 'MEDIUM')
    ),
    'issues', v_issues
  );
END;
$$;

-- ─── Tabla de corridas ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sentinel_rls_audits (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ran_at            timestamptz NOT NULL DEFAULT now(),
  scanned_at        timestamptz,
  total_tables      int NOT NULL DEFAULT 0,
  total_issues      int NOT NULL DEFAULT 0,
  severity_critical int NOT NULL DEFAULT 0,
  severity_high     int NOT NULL DEFAULT 0,
  severity_medium   int NOT NULL DEFAULT 0,
  issues            jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at        timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sentinel_rls_audits_created_at ON sentinel_rls_audits (created_at DESC);

ALTER TABLE sentinel_rls_audits ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "sentinel_rls_audits_service_role_all" ON sentinel_rls_audits;
CREATE POLICY "sentinel_rls_audits_service_role_all"
  ON sentinel_rls_audits FOR ALL TO service_role USING (true) WITH CHECK (true);

GRANT EXECUTE ON FUNCTION public.sentinel_rls_audit() TO service_role;
