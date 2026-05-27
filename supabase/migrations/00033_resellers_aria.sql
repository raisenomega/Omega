-- ╔══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00033 · DEBT-046 · resellers ARIA Premium support    ║
-- ╠══════════════════════════════════════════════════════════════════╣
-- ║  Adds aria_level + addons columns to resellers table so that    ║
-- ║  _resolve_role can return the real purchased ARIA level for      ║
-- ║  resellers (mirrors clients.aria_level + client_plans.addons).  ║
-- ╚══════════════════════════════════════════════════════════════════╝

ALTER TABLE resellers
  ADD COLUMN IF NOT EXISTS aria_level integer NOT NULL DEFAULT 3
    CHECK (aria_level BETWEEN 1 AND 4),
  ADD COLUMN IF NOT EXISTS addons jsonb NOT NULL DEFAULT '[]'::jsonb;

COMMENT ON COLUMN resellers.aria_level IS
  'ARIA intelligence level for this reseller (1-4). Default 3 (pro). '
  'Bumped to 4 when aria_premium_reseller addon is active.';

COMMENT ON COLUMN resellers.addons IS
  'JSONB array of active/deactivated addons. '
  'Schema: [{addon_code, stripe_subscription_id, activated_at, deactivated_at}]. '
  'Mirrors client_plans.addons pattern (DEBT-037/DEBT-046).';
