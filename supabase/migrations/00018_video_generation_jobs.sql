-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00018 · video_generation_jobs (DEBT-020 Sprint 2)       ║
-- ║  22 may 2026                                                       ║
-- ║                                                                    ║
-- ║  Background job pattern para Veo 3.1: POST /generate-video inserta ║
-- ║  row pending + APScheduler date trigger inmediato ejecuta worker.  ║
-- ║  Worker hace start+poll+download+upload (30-90s típico) sin        ║
-- ║  bloquear el HTTP request. GET /generate-video/{id} retorna status.║
-- ║                                                                    ║
-- ║  Limitaciones V1 documentadas como DEBT futura:                    ║
-- ║   · Memory jobstore · jobs en 'running' tras Railway restart=orphan║
-- ║   · Sin cron de cleanup · orphans visibles en query manual         ║
-- ║   · Sin rate limit por cliente · futuro max 3 pending concurrentes ║
-- ╚═══════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS video_generation_jobs (
  id           uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id    uuid        NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  prompt       text        NOT NULL,
  ratio        text        NOT NULL DEFAULT '1280:768',
  status       text        NOT NULL CHECK (status IN ('pending','running','completed','failed')),
  video_url    text,
  error        text,
  metadata     jsonb       NOT NULL DEFAULT '{}'::jsonb,
  created_at   timestamptz NOT NULL DEFAULT now(),
  started_at   timestamptz,
  completed_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_video_jobs_client_created
  ON video_generation_jobs (client_id, created_at DESC);

ALTER TABLE video_generation_jobs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS video_jobs_service_role ON video_generation_jobs;
CREATE POLICY video_jobs_service_role ON video_generation_jobs
  FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS video_jobs_owner_read ON video_generation_jobs;
CREATE POLICY video_jobs_owner_read ON video_generation_jobs
  FOR SELECT TO authenticated
  USING (client_id IN (SELECT id FROM clients WHERE user_id = (SELECT auth.uid())));

COMMENT ON TABLE video_generation_jobs IS
  'Background jobs para video Veo 3.1 · DEBT-020 Sprint 2. Lifecycle: pending → running → completed|failed. Orphan recovery cron pendiente (DEBT futura).';
