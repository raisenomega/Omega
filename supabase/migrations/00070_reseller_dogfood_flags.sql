-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00070 · flags por-reseller (dogfooding reseller@omega.com) ║
-- ║  20 jun 2026 · aditiva · idempotente (IF NOT EXISTS) · cero DROP.    ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- rex_live_enabled = 2da llave de REX (junto al maestro global REX_LIVE_ENABLED).
--   live = maestro_global AND este flag del reseller DUEÑO del cliente. Default false →
--   ningún reseller publica en vivo aunque sus clientes compren el add-on, salvo que el
--   owner lo encienda per-reseller. (DEBT-098 · per-reseller live.)
ALTER TABLE resellers ADD COLUMN IF NOT EXISTS rex_live_enabled boolean NOT NULL DEFAULT false;

-- default_client_aria_level = nivel ARIA que HEREDAN los clientes NUEVOS de este reseller
--   (lo aplica insert_client en el onboarding). NULL = sin override → el cliente cae al
--   DEFAULT del DB (clients.aria_level = 1). Por eso NO afecta a otros resellers (NULL).
ALTER TABLE resellers ADD COLUMN IF NOT EXISTS default_client_aria_level integer
  CHECK (default_client_aria_level IS NULL OR default_client_aria_level BETWEEN 1 AND 4);

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply:
--   SELECT column_name FROM information_schema.columns
--     WHERE table_name='resellers'
--     AND column_name IN ('rex_live_enabled','default_client_aria_level');
--   -- Esperado: 2 filas
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00070
-- ═══════════════════════════════════════════════════════════════════
