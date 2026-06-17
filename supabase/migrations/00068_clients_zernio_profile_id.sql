-- 00068 · zernio_profile_id en clients · B-2 (OAuth-vía-Zernio por negocio · profile aislado).
-- Cada negocio = un profile Zernio; sus cuentas conectadas viven aisladas en ese profile
-- (getConnectUrl es profile-scoped). NULL = el negocio aún no tiene profile creado.
-- Aditiva · reusa social_accounts.zernio_account_id/zernio_account_handle (00047). 17 jun 2026.
ALTER TABLE clients ADD COLUMN IF NOT EXISTS zernio_profile_id text;
COMMENT ON COLUMN clients.zernio_profile_id IS
  'Profile Zernio del negocio (B-2). Cada negocio aísla sus cuentas conectadas en su profile. NULL = sin profile aún.';
