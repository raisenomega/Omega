-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00046 · image_generation_jobs (DEBT-IMAGE-ASYNC · F1)    ║
-- ║  2 jun 2026                                                        ║
-- ║                                                                    ║
-- ║  Background job pattern para Nano Banana (espejo de 00018          ║
-- ║  video_generation_jobs). Motivo: generación de imagen mide 48s     ║
-- ║  Gemini puro (99.3%) · síncrono retiene la conexión HTTP del       ║
-- ║  cliente → timeout/UX congelada. Async: POST devuelve job_id,      ║
-- ║  worker (asyncio.create_task) genera+sube, frontend pollea.        ║
-- ║                                                                    ║
-- ║  ADITIVA · cero DROP · cero cambios al flujo de video (no se toca).║
-- ║  CHECK incluye 'cancelled' desde el inicio (el video lo agregó     ║
-- ║  después · acá nace correcto). image_url en vez de video_url ·     ║
-- ║  size/quality en vez de ratio. metadata jsonb: style/aspect/       ║
-- ║  apply_logo/logo_url/refs.                                         ║
-- ║                                                                    ║
-- ║  Limitación V1 heredada de video → DEBT-IMAGE-ASYNC-ORPHANS:       ║
-- ║   jobs 'running' huérfanos tras restart de Railway (sin cron       ║
-- ║   cleanup · F5 pendiente · no bloqueante).                         ║
-- ╚═══════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS image_generation_jobs (
  id           uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id    uuid        NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  prompt       text        NOT NULL,
  size         text        NOT NULL DEFAULT '1024x1024',
  quality      text        NOT NULL DEFAULT 'standard',
  status       text        NOT NULL CHECK (status IN ('pending','running','completed','failed','cancelled')),
  image_url    text,
  error        text,
  metadata     jsonb       NOT NULL DEFAULT '{}'::jsonb,
  created_at   timestamptz NOT NULL DEFAULT now(),
  started_at   timestamptz,
  completed_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_image_jobs_client_created
  ON image_generation_jobs (client_id, created_at DESC);

ALTER TABLE image_generation_jobs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS image_jobs_service_role ON image_generation_jobs;
CREATE POLICY image_jobs_service_role ON image_generation_jobs
  FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS image_jobs_owner_read ON image_generation_jobs;
CREATE POLICY image_jobs_owner_read ON image_generation_jobs
  FOR SELECT TO authenticated
  USING (client_id IN (SELECT id FROM clients WHERE user_id = (SELECT auth.uid())));

COMMENT ON TABLE image_generation_jobs IS
  'Background jobs para imagen Nano Banana · DEBT-IMAGE-ASYNC. Lifecycle: pending → running → completed|failed|cancelled. Espejo de video_generation_jobs (00018). Orphan recovery cron pendiente (DEBT-IMAGE-ASYNC-ORPHANS).';

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SELECT manual · NO aplicar sin OK CEO):
--   SELECT table_name FROM information_schema.tables
--     WHERE table_schema='public' AND table_name='image_generation_jobs';  -- 1 fila
--   SELECT count(*) FROM image_generation_jobs;  -- 0 (vacía tras migración)
-- ═══════════════════════════════════════════════════════════════════
