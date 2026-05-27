-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00037 · oauth_tokens (RONDA D · OAuth Meta + Google)    ║
-- ║  27 may 2026 · DEBT-040/003 · tokens OAuth per cliente+proveedor   ║
-- ║                                                                   ║
-- ║  access/refresh CIFRADOS a nivel app (Fernet · oauth/_token_crypto)║
-- ║   → aún con RLS read, el token viaja como ciphertext. RLS          ║
-- ║   client-scoped (cliente lee lo suyo · service_role FOR ALL).     ║
-- ║  Idempotente · aditiva (cero DROP de tablas).                     ║
-- ╚═══════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS oauth_tokens (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id            uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  provider             text NOT NULL CHECK (provider IN ('meta','google')),
  access_token_enc     text NOT NULL,               -- ciphertext Fernet
  refresh_token_enc    text,                          -- ciphertext Fernet
  scopes               text,
  external_account_id  text,                          -- page/account id del proveedor
  expires_at           timestamptz,
  metadata             jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at           timestamptz NOT NULL DEFAULT now(),
  updated_at           timestamptz NOT NULL DEFAULT now(),
  UNIQUE (client_id, provider)
);

CREATE INDEX IF NOT EXISTS idx_oauth_tokens_client_provider
  ON oauth_tokens (client_id, provider);

ALTER TABLE oauth_tokens ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "oauth_tokens inherits clients RLS" ON oauth_tokens;
CREATE POLICY "oauth_tokens inherits clients RLS"
  ON oauth_tokens FOR SELECT
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

DROP POLICY IF EXISTS "Service role manages oauth_tokens" ON oauth_tokens;
CREATE POLICY "Service role manages oauth_tokens"
  ON oauth_tokens FOR ALL
  USING (auth.role() = 'service_role');

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply:
--   SELECT policyname FROM pg_policies WHERE tablename='oauth_tokens';  -- 2 políticas
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00037
