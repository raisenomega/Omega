-- Pieza 3 · placement (story/feed) · 26 jun 2026.
-- scheduled_posts NO tiene columna metadata jsonb → columna dedicada para el flag de historia.
-- El agendado la estampa (build_fanout_rows / schedule_post); REX (publish_scheduled_post) la lee
-- y, SOLO para IG/FB, manda platformSpecificData.contentType:"story" a Zernio (estructura STEP 0 en vivo).
-- Forward-only · retrocompat total: default false = post normal = comportamiento de hoy intacto.
ALTER TABLE scheduled_posts
  ADD COLUMN IF NOT EXISTS is_story boolean NOT NULL DEFAULT false;
