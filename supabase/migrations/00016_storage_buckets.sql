-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00016 · Storage buckets generated-images + generated-videos
-- ║  22 may 2026 · Sprint 2 P1 · Cierre DEBT-018 · setup DEBT-019      ║
-- ║                                                                    ║
-- ║  Cubre 2 buckets en una migración para evitar 00017 inmediato.     ║
-- ║  Pattern idéntico a 00013_avatars (00012_brand_files variante con  ║
-- ║  per-folder access). Aquí: public read · service_role write.       ║
-- ║                                                                    ║
-- ║  Idempotente: ON CONFLICT DO NOTHING + DROP POLICY IF EXISTS       ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- Bucket generated-images · 10 MB · image/jpeg|png|webp
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'generated-images', 'generated-images', true, 10485760,
  ARRAY['image/jpeg','image/png','image/webp']
)
ON CONFLICT (id) DO NOTHING;

-- Bucket generated-videos · 500 MB · video/mp4
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'generated-videos', 'generated-videos', true, 524288000,
  ARRAY['video/mp4']
)
ON CONFLICT (id) DO NOTHING;

-- Public read · habilita fetch sin auth desde redes sociales (IG/FB/TikTok/
-- LinkedIn scrapean Open Graph como anon). Restringir a authenticated rompe
-- el share público. Writes/updates/deletes: service_role only (bypass RLS ·
-- no policy explícita necesaria · default deny para anon/authenticated).
DROP POLICY IF EXISTS "generated_images_public_read" ON storage.objects;
CREATE POLICY "generated_images_public_read" ON storage.objects FOR SELECT
  USING (bucket_id = 'generated-images');

DROP POLICY IF EXISTS "generated_videos_public_read" ON storage.objects;
CREATE POLICY "generated_videos_public_read" ON storage.objects FOR SELECT
  USING (bucket_id = 'generated-videos');
