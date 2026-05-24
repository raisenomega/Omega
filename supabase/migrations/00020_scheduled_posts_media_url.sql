-- DEBT-CL-017 + DEBT-031 partial cierre (23 may 2026 · Sprint 3).
-- Agrega media_url para soportar image OR video como adjunto del post
-- programado. El content_type del content_lab_generated FK desambigua
-- (image_url vs video_url eran 2 cols separadas en el handler legacy ·
-- aquí: 1 col semánticamente neutra).
-- Idempotente · safe en re-runs.

ALTER TABLE scheduled_posts
  ADD COLUMN IF NOT EXISTS media_url text;

COMMENT ON COLUMN scheduled_posts.media_url IS
  'URL pública del media adjunto (Supabase Storage). null si el post es texto puro. content_type del content_lab_generated FK determina si es image o video.';
