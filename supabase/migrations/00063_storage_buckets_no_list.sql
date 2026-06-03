-- 00063_storage_buckets_no_list.sql
-- Cierra 4 HIGH del Supabase Linter (broad SELECT en storage.objects permite LIST/enumeración).
-- Approach verificado contra uso REAL del frontend (no el ejemplo genérico):
--   · avatars / generated-images / generated-videos: el frontend solo usa getPublicUrl (CDN · buckets
--     public=true · NO requiere policy SELECT) → DROP de la broad *_public_read cierra el LIST sin romper nada.
--   · media: Media.tsx hace .list() per-user → reemplazar broad por folder-scoped (own {uid}/) preserva
--     el listado propio y bloquea enumeración cross-tenant.
-- getPublicUrl sigue funcionando en los 4 (buckets quedan public=true · CDN no usa RLS).

DROP POLICY IF EXISTS avatars_public_read ON storage.objects;
DROP POLICY IF EXISTS generated_images_public_read ON storage.objects;
DROP POLICY IF EXISTS generated_videos_public_read ON storage.objects;

DROP POLICY IF EXISTS media_public_read ON storage.objects;
DROP POLICY IF EXISTS media_user_select ON storage.objects;
CREATE POLICY media_user_select ON storage.objects
  FOR SELECT
  TO authenticated
  USING (bucket_id = 'media' AND (storage.foldername(name))[1] = auth.uid()::text);

-- ═══════════════════════════════════════════════════════════════════
-- Verificación:  SELECT policyname FROM pg_policies WHERE schemaname='storage' AND tablename='objects'
--                  AND policyname LIKE '%public_read%';  -- esperado: 0 filas (broad SELECT eliminadas)
-- ═══════════════════════════════════════════════════════════════════
