-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00013 · Storage bucket avatars (Settings V2 · Tab 1)   ║
-- ║  20 may 2026 · ProfileSection avatar upload                       ║
-- ║  Idempotente: ON CONFLICT + DROP POLICY IF EXISTS                 ║
-- ╚═══════════════════════════════════════════════════════════════════╝

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'avatars', 'avatars', true, 5242880,
  ARRAY['image/png','image/jpeg','image/webp','image/gif']
)
ON CONFLICT (id) DO NOTHING;

-- Solo el propio user puede subir/actualizar SU avatar (folder = user_id).
DROP POLICY IF EXISTS "avatars_user_upload" ON storage.objects;
CREATE POLICY "avatars_user_upload" ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'avatars' AND (storage.foldername(name))[1] = (SELECT auth.uid())::text);

DROP POLICY IF EXISTS "avatars_user_update" ON storage.objects;
CREATE POLICY "avatars_user_update" ON storage.objects FOR UPDATE
  USING (bucket_id = 'avatars' AND (storage.foldername(name))[1] = (SELECT auth.uid())::text);

-- Public read · sidebar muestra avatares sin signed URLs.
DROP POLICY IF EXISTS "avatars_public_read" ON storage.objects;
CREATE POLICY "avatars_public_read" ON storage.objects FOR SELECT
  USING (bucket_id = 'avatars');
