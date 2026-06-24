-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00074 · owner_accounts (cuentas-dueño exentas)          ║
-- ║  24 jun 2026 · flag per-user PERMANENTE (vitalicio · NO parche)    ║
-- ║                                                                   ║
-- ║  Marca user_ids del DUEÑO exentos de: paywall de creación de       ║
-- ║  negocio + add-on de REX (rex_addon_active). Exime de PAGOS,       ║
-- ║  NUNCA de aislamiento (resolve_client_or_403/user_owns_client      ║
-- ║  siguen mandando). La lee SOLO el backend con service-role.        ║
-- ║  Consumo del flag = commits posteriores (esta migr solo crea+siembra).║
-- ║  Idempotente · aditiva (cero DROP de tablas). Ver SOURCE_OF_TRUTH §6.║
-- ╚═══════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS owner_accounts (
  user_id     uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  note        text,                                    -- por qué está exenta
  created_at  timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE owner_accounts IS
  'Cuentas del dueño exentas de paywall/add-on REX · permanentes por diseño · NO parche · ver SOURCE_OF_TRUTH §6';

ALTER TABLE owner_accounts ENABLE ROW LEVEL SECURITY;

-- Service-role only: la lee/escribe el backend (service_role), NUNCA el cliente directo.
-- Patrón verbatim de 00037_oauth_tokens ("Service role manages …" · FOR ALL · service_role).
DROP POLICY IF EXISTS "Service role manages owner_accounts" ON owner_accounts;
CREATE POLICY "Service role manages owner_accounts"
  ON owner_accounts FOR ALL
  USING (auth.role() = 'service_role');

-- ─── Siembra idempotente · las 2 cuentas-dueño (UUIDs LEÍDOS de la DB, no adivinados) ───
INSERT INTO owner_accounts (user_id, note) VALUES
  ('61f88b91-dbf9-4f21-9c31-aecbcbc6f52e', 'reseller@omega.com · cuenta dueño'),
  ('84d86286-e36e-4942-a312-0d65aab4bbe7', 'raisen@omega.com · cuenta dueño')
ON CONFLICT (user_id) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (manual · NO ejecuta acá):
--   SELECT user_id, note FROM owner_accounts;                       -- 2 filas
--   SELECT policyname FROM pg_policies WHERE tablename='owner_accounts';  -- 1 política
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00074
