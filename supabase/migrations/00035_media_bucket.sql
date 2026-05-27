-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00035 · Storage bucket media (DEBT-060 · Biblioteca)    ║
-- ║  27 may 2026 · Media.tsx usaba el bucket 'media' inexistente.      ║
-- ║                                                                   ║
-- ║  Folder-scoped por auth.uid() (patrón avatars 00013 / brand-files ║
-- ║  00012) → AISLAMIENTO por cuenta: cada usuario sube/lista/borra    ║
-- ║  SOLO su carpeta {uid}/. Sin esto, cualquier authenticated podría  ║
-- ║  leer/borrar media de otro (fuga cross-tenant · G3). Media.tsx se  ║
-- ║  actualiza en el mismo commit para namespacear bajo {uid}/.        ║
-- ║  Public read (imágenes vía getPublicUrl · sin signed URLs · misma  ║
-- ║  postura que avatars/generated-images).                           ║
-- ║  Idempotente: ON CONFLICT + DROP POLICY IF EXISTS · aditiva.       ║
-- ╚═══════════════════════════════════════════════════════════════════╝

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'media', 'media', true, 524288000,
  ARRAY[
    'image/jpeg','image/png','image/webp','image/gif',
    'video/mp4','video/webm','video/quicktime'
  ]
)
ON CONFLICT (id) DO NOTHING;

-- Escritura/borrado: solo en la carpeta propia ({uid}/...) · aislamiento cross-tenant.
DROP POLICY IF EXISTS "media_user_insert" ON storage.objects;
CREATE POLICY "media_user_insert" ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'media' AND (storage.foldername(name))[1] = (SELECT auth.uid())::text);

DROP POLICY IF EXISTS "media_user_update" ON storage.objects;
CREATE POLICY "media_user_update" ON storage.objects FOR UPDATE
  USING (bucket_id = 'media' AND (storage.foldername(name))[1] = (SELECT auth.uid())::text);

DROP POLICY IF EXISTS "media_user_delete" ON storage.objects;
CREATE POLICY "media_user_delete" ON storage.objects FOR DELETE
  USING (bucket_id = 'media' AND (storage.foldername(name))[1] = (SELECT auth.uid())::text);

-- Public read · la galería muestra imágenes vía getPublicUrl (igual avatars/generated-images).
DROP POLICY IF EXISTS "media_public_read" ON storage.objects;
CREATE POLICY "media_public_read" ON storage.objects FOR SELECT
  USING (bucket_id = 'media');

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SQL Editor):
--   SELECT id, public FROM storage.buckets WHERE id='media';        -- 1 fila · public=true
--   SELECT policyname, cmd FROM pg_policies WHERE schemaname='storage'
--     AND tablename='objects' AND policyname LIKE 'media_%';        -- 4 políticas
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00035
-- ═══════════════════════════════════════════════════════════════════
