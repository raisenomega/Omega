-- ═══════════════════════════════════════════════════════════════════
-- OmegaRaisen — Migración 00022: GUARDIAN security (SPRINT 4B-1)
-- Spec: GUARDIAN_SECURITY_AGENT.md (firmado 24 may 2026 · gitignored).
-- Seguridad de usuario/sesión (≠ SENTINEL infra). 3 tablas + RLS.
-- Superadmin (decisión §7.5): resellers.owner_user_id + flag is_owner.
-- ═══════════════════════════════════════════════════════════════════

-- ─── Superadmin flag (§7.5) ───────────────────────────────────────
ALTER TABLE resellers ADD COLUMN IF NOT EXISTS is_owner boolean NOT NULL DEFAULT false;

-- ─── user_security_log · append-only · evento auth/sesión ─────────
CREATE TABLE IF NOT EXISTS user_security_log (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  client_id     uuid REFERENCES clients(id) ON DELETE SET NULL,
  reseller_id   uuid REFERENCES resellers(id) ON DELETE SET NULL,
  event_type    text NOT NULL CHECK (event_type IN (
                   'login_success','login_failed','logout','session_refresh',
                   'password_reset','new_device','suspicious_activity')),
  ip_address    text,
  user_agent    text,
  country       text,                                  -- geo → fase posterior (§7.6)
  geo           jsonb NOT NULL DEFAULT '{}'::jsonb,
  risk_score    integer NOT NULL DEFAULT 0 CHECK (risk_score BETWEEN 0 AND 100),
  metadata      jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_usl_user_time ON user_security_log(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usl_event ON user_security_log(event_type);
CREATE INDEX IF NOT EXISTS idx_usl_ip ON user_security_log(ip_address);

ALTER TABLE user_security_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "usl_owner_read" ON user_security_log FOR SELECT USING (
  user_id = auth.uid()
  OR client_id IN (SELECT id FROM clients WHERE user_id = auth.uid())
  OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  OR auth.uid() IN (SELECT owner_user_id FROM resellers WHERE is_owner = true)
);
CREATE POLICY "usl_service_write" ON user_security_log FOR INSERT
  WITH CHECK (auth.role() = 'service_role');

-- ─── ip_watchlist · allow/deny/watch (cross-tenant infra) ─────────
CREATE TABLE IF NOT EXISTS ip_watchlist (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ip_address      text NOT NULL,
  list_type       text NOT NULL CHECK (list_type IN ('block','allow','watch')),
  reason          text,
  scope_client_id uuid REFERENCES clients(id) ON DELETE CASCADE,  -- NULL = global
  created_by      uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  expires_at      timestamptz,
  created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_ipw_ip ON ip_watchlist(ip_address);
CREATE INDEX IF NOT EXISTS idx_ipw_type ON ip_watchlist(list_type);

ALTER TABLE ip_watchlist ENABLE ROW LEVEL SECURITY;
CREATE POLICY "ipw_superadmin_read" ON ip_watchlist FOR SELECT USING (
  auth.uid() IN (SELECT owner_user_id FROM resellers WHERE is_owner = true)
);
CREATE POLICY "ipw_service_all" ON ip_watchlist FOR ALL
  USING (auth.role() = 'service_role') WITH CHECK (auth.role() = 'service_role');

-- ─── security_incidents · incidentes discretos ───────────────────
CREATE TABLE IF NOT EXISTS security_incidents (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  client_id     uuid REFERENCES clients(id) ON DELETE CASCADE,
  reseller_id   uuid REFERENCES resellers(id) ON DELETE CASCADE,
  incident_type text NOT NULL CHECK (incident_type IN (
                   'brute_force','impossible_travel','credential_stuffing',
                   'anomalous_session','account_takeover_suspected')),
  severity      text NOT NULL CHECK (severity IN ('low','medium','high','critical')),
  status        text NOT NULL DEFAULT 'open' CHECK (status IN (
                   'open','investigating','resolved','false_positive')),
  summary       text,
  evidence      jsonb NOT NULL DEFAULT '{}'::jsonb,
  detected_at   timestamptz NOT NULL DEFAULT now(),
  resolved_at   timestamptz,
  resolved_by   uuid REFERENCES auth.users(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_si_user ON security_incidents(user_id);
CREATE INDEX IF NOT EXISTS idx_si_client ON security_incidents(client_id);
CREATE INDEX IF NOT EXISTS idx_si_status_sev ON security_incidents(status, severity);
CREATE INDEX IF NOT EXISTS idx_si_detected ON security_incidents(detected_at DESC);

ALTER TABLE security_incidents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "si_owner_read" ON security_incidents FOR SELECT USING (
  user_id = auth.uid()
  OR client_id IN (SELECT id FROM clients WHERE user_id = auth.uid())
  OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  OR auth.uid() IN (SELECT owner_user_id FROM resellers WHERE is_owner = true)
);
CREATE POLICY "si_service_write" ON security_incidents FOR INSERT
  WITH CHECK (auth.role() = 'service_role');
CREATE POLICY "si_resolve" ON security_incidents FOR UPDATE USING (
  auth.role() = 'service_role'
  OR auth.uid() IN (SELECT owner_user_id FROM resellers WHERE is_owner = true)
) WITH CHECK (
  auth.role() = 'service_role'
  OR auth.uid() IN (SELECT owner_user_id FROM resellers WHERE is_owner = true)
);

-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00022
-- ═══════════════════════════════════════════════════════════════════
