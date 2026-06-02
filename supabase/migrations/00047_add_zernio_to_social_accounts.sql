-- 00047_add_zernio_to_social_accounts.sql
-- F5/2b · mapeo per-negocio per-plataforma de la cuenta Zernio.
-- ADITIVO (NULL allowed · IF NOT EXISTS idempotente): negocios sin mapeo siguen
-- con el fallback en vivo del resolver (FASE 2a · zernio_resolver.py). Cero backfill,
-- cero breaking change, sin cambio de RLS (hereda la policy existente de social_accounts).
ALTER TABLE social_accounts
  ADD COLUMN IF NOT EXISTS zernio_account_id     text,
  ADD COLUMN IF NOT EXISTS zernio_account_handle text;

-- Lookup del mapeo por (client_id, platform) solo cuando hay mapeo (partial index).
CREATE INDEX IF NOT EXISTS idx_social_accounts_zernio
  ON social_accounts (client_id, platform)
  WHERE zernio_account_id IS NOT NULL;
