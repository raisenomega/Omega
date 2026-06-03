-- 00051_sentinel_secrets_log.sql
-- SENTINEL Capa 5 · log de rotaciones de secrets (solo NOMBRE + timestamp · NUNCA el valor).
-- rotated_at NULL = baseline desconocido (seed inicial · señal suave MEDIUM, no urgente).
-- RLS solo service_role. Aditiva.

CREATE TABLE IF NOT EXISTS sentinel_secrets_log (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  secret_name text NOT NULL,
  rotated_at  timestamptz,                      -- NULL = baseline_unknown
  rotated_by  uuid,                             -- auth.users.id (NULL en seed)
  note        text,                             -- baseline_unknown | manual_rotation | ...
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sentinel_secrets_log_name_rotated
  ON sentinel_secrets_log (secret_name, rotated_at DESC);

ALTER TABLE sentinel_secrets_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "sentinel_secrets_log_service_role_all" ON sentinel_secrets_log;
CREATE POLICY "sentinel_secrets_log_service_role_all"
  ON sentinel_secrets_log
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Seed baseline_unknown · 1 fila por secret monitoreado (idempotente: solo si la tabla está vacía).
INSERT INTO sentinel_secrets_log (secret_name, rotated_at, note)
SELECT name, NULL::timestamptz, 'baseline_unknown'
FROM (VALUES
  ('ANTHROPIC_API_KEY'), ('SUPABASE_SERVICE_ROLE_KEY'), ('STRIPE_SECRET_KEY'),
  ('STRIPE_WEBHOOK_SECRET'), ('GOOGLE_CLIENT_SECRET'), ('SENTINEL_TOKEN'),
  ('SUPABASE_JWT_SECRET'), ('TOKEN_ENCRYPTION_KEY'), ('BRAVE_API_KEY'), ('RESEND_API_KEY')
) AS s(name)
WHERE NOT EXISTS (SELECT 1 FROM sentinel_secrets_log);
