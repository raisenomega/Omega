-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00017 · client_brand_dna table + trigger invalidation   ║
-- ║  22 may 2026 · DEBT-044 (Sprint 2)                                 ║
-- ║                                                                    ║
-- ║  Persiste BrandDNA computado por cliente · cron 3am recomputa      ║
-- ║  proactivamente · trigger SQL invalida last_computed_at cuando     ║
-- ║  brand_voice_corpus cambia (INSERT/UPDATE/DELETE).                 ║
-- ║                                                                    ║
-- ║  Lectura: use_brand_dna.build_dna_for_client lee tabla primero ·   ║
-- ║  recompute si last_computed_at IS NULL o >24h ago.                 ║
-- ╚═══════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS client_brand_dna (
  client_id        uuid        PRIMARY KEY REFERENCES clients(id) ON DELETE CASCADE,
  dna_jsonb        jsonb       NOT NULL,
  score            float       NOT NULL,
  last_computed_at timestamptz,
  last_corpus_size integer     NOT NULL DEFAULT 0,
  created_at       timestamptz NOT NULL DEFAULT now(),
  updated_at       timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE client_brand_dna ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS client_brand_dna_service_role ON client_brand_dna;
CREATE POLICY client_brand_dna_service_role ON client_brand_dna
  FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS client_brand_dna_owner_read ON client_brand_dna;
CREATE POLICY client_brand_dna_owner_read ON client_brand_dna
  FOR SELECT TO authenticated
  USING (client_id IN (SELECT id FROM clients WHERE user_id = (SELECT auth.uid())));

CREATE OR REPLACE FUNCTION invalidate_brand_dna_on_corpus_change()
RETURNS trigger AS $$
BEGIN
  UPDATE client_brand_dna
    SET last_computed_at = NULL
    WHERE client_id = COALESCE(NEW.client_id, OLD.client_id);
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS trg_invalidate_brand_dna ON brand_voice_corpus;
CREATE TRIGGER trg_invalidate_brand_dna
  AFTER INSERT OR UPDATE OR DELETE ON brand_voice_corpus
  FOR EACH ROW
  EXECUTE FUNCTION invalidate_brand_dna_on_corpus_change();

COMMENT ON TABLE client_brand_dna IS
  'BrandDNA persistido por cliente · DEBT-044 cerrada Sprint 2. last_computed_at=NULL → stale (recompute next read). Refresh proactivo: cron brand_dna_refresh 3am.';
