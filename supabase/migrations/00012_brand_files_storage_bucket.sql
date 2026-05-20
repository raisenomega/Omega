-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00012 · Storage bucket brand-files + RLS (DEBT-041)    ║
-- ║  20 may 2026 · cierra DEBT-041                                    ║
-- ║  Idempotente: ON CONFLICT + DROP POLICY IF EXISTS                 ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── Bucket privado · 10 MB · whitelist MIME ─────────────────────────
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'brand-files', 'brand-files', false, 10485760,
  ARRAY['image/png','image/jpeg','image/webp','image/svg+xml','application/pdf']
)
ON CONFLICT (id) DO NOTHING;

-- ─── RLS · path pattern {client_id}/{uuid}.{ext} ─────────────────────
DROP POLICY IF EXISTS "brand_files_client_select" ON storage.objects;
CREATE POLICY "brand_files_client_select" ON storage.objects FOR SELECT
  USING (bucket_id = 'brand-files' AND (storage.foldername(name))[1] IN (
    SELECT id::text FROM clients WHERE user_id = (SELECT auth.uid())
       OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = (SELECT auth.uid()))
  ));

DROP POLICY IF EXISTS "brand_files_client_insert" ON storage.objects;
CREATE POLICY "brand_files_client_insert" ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'brand-files' AND (storage.foldername(name))[1] IN (
    SELECT id::text FROM clients WHERE user_id = (SELECT auth.uid())
       OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = (SELECT auth.uid()))
  ));

DROP POLICY IF EXISTS "brand_files_service_all" ON storage.objects;
CREATE POLICY "brand_files_service_all" ON storage.objects FOR ALL
  USING (bucket_id = 'brand-files' AND auth.role() = 'service_role');
