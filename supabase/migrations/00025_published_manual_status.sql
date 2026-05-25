-- 00025_published_manual_status.sql (25 may 2026)
-- Agrega 'published_manual' al CHECK de scheduled_posts.status.
-- Distingue publicación MANUAL (el operador marca el post como publicado a mano,
-- feature popup calendario) de 'published' (auto/sistema vía MCP cuando esté activo).
-- La distinción es necesaria para analytics + aprendizaje del sistema (P5):
-- reusar 'published' mezclaría ambos orígenes y rompería reportes futuros.
--
-- Robusto (guardian MEDIA): descubre el CHECK real por catálogo en vez de asumir el
-- nombre auto-generado (scheduled_posts_status_check). Si algún entorno divergió de
-- 00001, igual lo encuentra y lo reemplaza. Idempotente · safe en re-runs.

DO $$
DECLARE c text;
BEGIN
  SELECT con.conname INTO c
  FROM pg_constraint con
  JOIN pg_class rel ON rel.oid = con.conrelid
  WHERE rel.relname = 'scheduled_posts'
    AND con.contype = 'c'
    AND pg_get_constraintdef(con.oid) ILIKE '%status%';
  IF c IS NOT NULL THEN
    EXECUTE format('ALTER TABLE scheduled_posts DROP CONSTRAINT %I', c);
  END IF;
END $$;

ALTER TABLE scheduled_posts ADD CONSTRAINT scheduled_posts_status_check
  CHECK (status IN ('pending','publishing','published','failed','cancelled','published_manual'));
