-- ═══════════════════════════════════════════════════════════════════
-- OmegaRaisen — Migración 00004: Anti-fraud signals + uniqueness guards
-- · Implementa R1 (1 trial por email/device) del MODELO_NEGOCIO_OMEGA_CLIENTE.md
-- · Bloquea reuso de cuentas sociales entre clients (typical fraud vector)
-- · Tabla anti_fraud_signals para auditar señales y triage manual
-- · R5: cliente final NO ve sus señales — solo Owner/Reseller/service_role
-- ═══════════════════════════════════════════════════════════════════

-- ─── 1. device_fingerprint en clients ─────────────────────────────
-- Captura post-creación de cliente; partial unique permite NULL en filas legacy.
ALTER TABLE clients
  ADD COLUMN IF NOT EXISTS device_fingerprint text;

CREATE UNIQUE INDEX IF NOT EXISTS uq_clients_device_fingerprint
  ON clients (device_fingerprint)
  WHERE device_fingerprint IS NOT NULL;

-- ─── 2. UNIQUE global en social_accounts (platform, account_id) ───
-- Hoy social_accounts tiene UNIQUE(client_id, platform, account_id) — eso permite
-- que el mismo IG @xyz exista en 2 clients. Nuevo índice global lo bloquea.
-- Conservamos el constraint original (redundante pero no removemos en este step).
CREATE UNIQUE INDEX IF NOT EXISTS uq_social_accounts_global
  ON social_accounts (platform, account_id)
  WHERE account_id IS NOT NULL;

-- ─── 3. TABLA anti_fraud_signals ──────────────────────────────────
CREATE TABLE IF NOT EXISTS anti_fraud_signals (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  -- client_id NULL = señal pre-creación de cliente (capturada durante signup)
  client_id       uuid REFERENCES clients(id) ON DELETE CASCADE,
  signal_type     text NOT NULL CHECK (signal_type IN (
    'email_duplicate_trial',          -- mismo email intentó trial 2x (auth.users ya bloquea, auditamos intentos)
    'device_fingerprint_duplicate',   -- mismo device con 2+ clients
    'ip_burst_signup',                -- N signups del mismo IP en ventana corta
    'social_account_collision',       -- cuenta social ya registrada en otro client
    'payment_method_reuse',           -- mismo Stripe payment method en multiple trials
    'velocity_anomaly',               -- velocidad de signups anómala
    'geo_inconsistency'               -- IP geo no matchea región declarada del cliente
  )),
  signal_value    text NOT NULL,                                   -- valor disparador en plano (email/fingerprint/IP) — facilita investigación
  severity        text NOT NULL DEFAULT 'medium' CHECK (severity IN ('low','medium','high','critical')),
  auto_blocked    boolean NOT NULL DEFAULT false,
  -- INVARIANT: severity='critical' implica auto_blocked=true (decisión Ibrain 18 may 2026)
  CONSTRAINT chk_critical_must_block CHECK (severity != 'critical' OR auto_blocked = true),
  detected_at     timestamptz NOT NULL DEFAULT now(),
  resolved        boolean NOT NULL DEFAULT false,
  resolved_at     timestamptz,
  resolved_by     uuid REFERENCES auth.users(id),
  resolution_note text,
  -- Extra context: user_agent, headers, related_client_ids[], request_id, etc.
  metadata        jsonb NOT NULL DEFAULT '{}'::jsonb
);

-- NOTA (responsabilidad app-layer · no SQL):
-- Cuando severity='critical' el backend DEBE notificar a Ibrain vía SENTINEL.
-- El INSERT con severity='critical' fuerza auto_blocked=true (CHECK arriba) pero
-- el envío de notificación SENTINEL queda al servicio que inserta la fila.

CREATE INDEX idx_antifraud_client     ON anti_fraud_signals (client_id)     WHERE client_id IS NOT NULL;
CREATE INDEX idx_antifraud_type       ON anti_fraud_signals (signal_type);
CREATE INDEX idx_antifraud_unresolved ON anti_fraud_signals (resolved)      WHERE resolved = false;
CREATE INDEX idx_antifraud_detected   ON anti_fraud_signals (detected_at DESC);

ALTER TABLE anti_fraud_signals ENABLE ROW LEVEL SECURITY;

-- service_role: full access (backend inserta vía service role)
CREATE POLICY "anti_fraud service role full"
  ON anti_fraud_signals FOR ALL
  USING (auth.role() = 'service_role');

-- Reseller dueño del cliente: SELECT de las señales de SUS clients
-- Patrón (SELECT auth.uid()) evita re-evaluación por fila (Auth RLS Init Plan optim)
CREATE POLICY "anti_fraud reseller view"
  ON anti_fraud_signals FOR SELECT
  USING (
    client_id IN (
      SELECT id FROM clients
      WHERE reseller_id IN (
        SELECT id FROM resellers WHERE owner_user_id = (SELECT auth.uid())
      )
    )
  );

-- Reseller dueño: UPDATE para resolver señales (resolved=true, resolution_note)
CREATE POLICY "anti_fraud reseller resolve"
  ON anti_fraud_signals FOR UPDATE
  USING (
    client_id IN (
      SELECT id FROM clients
      WHERE reseller_id IN (
        SELECT id FROM resellers WHERE owner_user_id = (SELECT auth.uid())
      )
    )
  );

-- Cliente final (auth.uid() = clients.user_id): SIN POLICY = sin acceso (R5)
-- Solo Owner/Reseller/service_role pueden ver y resolver señales.
