-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00029 · sentinel_persistence                          ║
-- ║  26 may 2026 · SENTINEL · persistencia del bucle de mejora        ║
-- ║                                                                   ║
-- ║  Propósito: materializa las 3 tablas que persistence_service.py   ║
-- ║   escribe/lee y que faltaban en migraciones (tablas fantasma):    ║
-- ║   sentinel_risk_scores · omega_tech_debt · omega_error_registry   ║
-- ║                                                                   ║
-- ║  RLS habilitada · solo service_role (tablas internas de SENTINEL  ║
-- ║   · backend-only · sin acceso de cliente).                        ║
-- ║  Aditiva: cero DROP de tablas · cero modificaciones destructivas. ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── sentinel_risk_scores · Risk Score calculado por SENT_BRAIN ──────
CREATE TABLE IF NOT EXISTS sentinel_risk_scores (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  score               double precision NOT NULL,
  security_score      double precision,
  architecture_score  double precision,
  performance_score   double precision,
  quality_score       double precision,
  deployment_score    double precision,
  documentation_score double precision,
  verdict             text NOT NULL,
  issues_critical     integer NOT NULL DEFAULT 0,
  issues_high         integer NOT NULL DEFAULT 0,
  issues_medium       integer NOT NULL DEFAULT 0,
  issues_low          integer NOT NULL DEFAULT 0,
  auto_fixes_applied  integer NOT NULL DEFAULT 0,
  calculated_at       timestamptz NOT NULL DEFAULT now(),
  created_at          timestamptz NOT NULL DEFAULT now()
);

-- Índice para get_summary: último score por calculated_at DESC.
CREATE INDEX IF NOT EXISTS idx_sentinel_risk_scores_calculated_at
  ON sentinel_risk_scores (calculated_at DESC);

-- ─── omega_tech_debt · registro de deuda técnica ─────────────────────
CREATE TABLE IF NOT EXISTS omega_tech_debt (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  debt_id      text NOT NULL UNIQUE,
  description  text NOT NULL,
  priority     text,
  status       text NOT NULL DEFAULT 'active',
  resolution   text,
  resolved_at  timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now()
);

-- Índice para get_summary: filtra por status = 'active'.
CREATE INDEX IF NOT EXISTS idx_omega_tech_debt_status
  ON omega_tech_debt (status);

-- ─── omega_error_registry · bugs resueltos → reglas permanentes ──────
CREATE TABLE IF NOT EXISTS omega_error_registry (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  error_id         text NOT NULL UNIQUE,
  error_type       text NOT NULL,
  file_path        text,
  symptom          text,
  root_cause       text,
  fix_description  text,
  rule_code        text,
  rule_text        text,
  prevention       text,
  commit_hash      text,
  registered_by    text NOT NULL DEFAULT 'IBRAIN',
  registered_at    timestamptz NOT NULL DEFAULT now(),
  created_at       timestamptz NOT NULL DEFAULT now()
);

-- Índice para get_summary: count por error_type.
CREATE INDEX IF NOT EXISTS idx_omega_error_registry_error_type
  ON omega_error_registry (error_type);

-- ─── RLS · solo service_role (tablas internas backend-only) ──────────
ALTER TABLE sentinel_risk_scores  ENABLE ROW LEVEL SECURITY;
ALTER TABLE omega_tech_debt       ENABLE ROW LEVEL SECURITY;
ALTER TABLE omega_error_registry  ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Service role manages sentinel_risk_scores" ON sentinel_risk_scores;
CREATE POLICY "Service role manages sentinel_risk_scores"
  ON sentinel_risk_scores FOR ALL
  USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Service role manages omega_tech_debt" ON omega_tech_debt;
CREATE POLICY "Service role manages omega_tech_debt"
  ON omega_tech_debt FOR ALL
  USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Service role manages omega_error_registry" ON omega_error_registry;
CREATE POLICY "Service role manages omega_error_registry"
  ON omega_error_registry FOR ALL
  USING (auth.role() = 'service_role');

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SELECT manual en SQL Editor):
--   SELECT table_name FROM information_schema.tables
--     WHERE table_schema = 'public'
--     AND table_name IN ('sentinel_risk_scores','omega_tech_debt','omega_error_registry');
--   -- Esperado: 3 filas
--
--   SELECT indexname FROM pg_indexes
--     WHERE tablename IN ('sentinel_risk_scores','omega_tech_debt','omega_error_registry');
--   -- Esperado: 3 pkeys + idx_sentinel_risk_scores_calculated_at
--   --           + idx_omega_tech_debt_status + idx_omega_error_registry_error_type
--
--   SELECT count(*) FROM sentinel_risk_scores;
--   SELECT count(*) FROM omega_tech_debt;
--   SELECT count(*) FROM omega_error_registry;
--   -- Esperado: 0 (tablas vacías tras migración)
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00029
-- ═══════════════════════════════════════════════════════════════════
