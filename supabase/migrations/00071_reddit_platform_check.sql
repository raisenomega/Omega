-- 00071 · permitir 'reddit' en social_accounts.platform (tab Cuentas de ARIA · NO modal §7).
--
-- Arco Reddit: el tab Cuentas ofrece Reddit como red conectable (Zernio da authUrl · connect
-- backend genérico). Sin este CHECK ampliado, el insert de una cuenta reddit fallaría con
-- error de constraint = bug en vivo. REGLA DE ORDEN DE DEPLOY: esta migración va a prod ANTES
-- de pushear el frontend que ofrece Reddit (mismo patrón IMAGE-ASYNC: migración primero).
--
-- 3 capas que NO deben desincronizarse (ver DEBT-PLATFORMS-PINTEREST-SNAPCHAT-THREADS-BLUESKY):
--   (1) src/lib/social-platforms-tab.ts CONNECTABLE_PLATFORMS  (2) este CHECK  (3) onboarding §7
-- El test src/test/socialPlatformsCheckSync.test.ts ATA (1)<->(2): falla si divergen.
--
-- Dry-run read-only previo (21 jun 2026 · prod rwlnihoqhxwpbehibgxu): CHECK actual = 6 redes ·
-- 0 filas existentes violan el set nuevo (fb=5 ig=5 li=1 tt=3 tw=3) → migración segura. Además
-- ADD CONSTRAINT revalida las filas existentes: si alguna violara, la transacción aborta sola.

ALTER TABLE public.social_accounts DROP CONSTRAINT IF EXISTS social_accounts_platform_check;

ALTER TABLE public.social_accounts ADD CONSTRAINT social_accounts_platform_check
  CHECK (platform IN ('instagram', 'facebook', 'tiktok', 'twitter', 'linkedin', 'youtube', 'reddit'));
