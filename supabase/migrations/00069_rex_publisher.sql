-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00069 · REX Publicador Autónomo (DEBT-098 · Fase 0)    ║
-- ║  20 jun 2026 · estado de gating + auditoría append-only           ║
-- ║                                                                   ║
-- ║  Aditiva · idempotente (IF NOT EXISTS) · cero DROP destructivo.   ║
-- ║  RLS hereda patrón clients (G5 · espejo 00027/00067).             ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── clients · flags de REX ──────────────────────────────────────────
-- rex_addon_active   = ¿el cliente COMPRÓ el add-on "Modo Autónomo"?
--                      (lo flipea el handler de billing al activarse publisher_*)
-- autonomous_mode_on = ¿el humano ENCENDIÓ el toggle? (consentimiento · distinto
--                      de la compra · default OFF · lo setea el owner/reseller)
-- crisis_active      = kill-switch MANUAL de crisis por cliente (P1 · honesto · NO
--                      finge detección automática). Si true, REX holdea TODAS las
--                      publicaciones autónomas de ese cliente al instante. El cableado
--                      automático (crisis_manager lo enciende solo) = DEBT-REX-CRISIS-AUTO.
-- Las 3 son columnas de `clients` → HEREDAN su RLS: "Resellers manage their clients"
-- (owner/reseller escriben · su kill-switch) + "Service role manages clients" (el
-- worker REX lee con service_role). No requieren policy nueva.
ALTER TABLE clients ADD COLUMN IF NOT EXISTS rex_addon_active   boolean NOT NULL DEFAULT false;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS autonomous_mode_on boolean NOT NULL DEFAULT false;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS crisis_active      boolean NOT NULL DEFAULT false;

-- ─── rex_publish_log · auditoría append-only de cada decisión REX ────
-- Una fila por post evaluado: publish (se intentó publicar) o hold (gate lo frenó).
-- scheduled_post_id SIN FK (audit durable · sobrevive a borrado del post).
-- was_correct queda creada hoy (NULL) para que F3 (Loop 2) no migre dos veces.
CREATE TABLE IF NOT EXISTS rex_publish_log (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id          uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  scheduled_post_id  uuid,
  platform           text,
  published_at       timestamptz,
  scheduled_for      timestamptz,
  gate_result        text NOT NULL CHECK (gate_result IN ('publish','hold')),
  hold_reason        text,
  brand_voice_score  numeric(3,2),
  was_correct        boolean,
  created_at         timestamptz NOT NULL DEFAULT now()
);

-- ─── Índice owner-read (más reciente por cliente) ────────────────────
CREATE INDEX IF NOT EXISTS idx_rex_publish_log_client_time
  ON rex_publish_log(client_id, created_at DESC);

-- ─── RLS (espejo 00027) ──────────────────────────────────────────────
ALTER TABLE rex_publish_log ENABLE ROW LEVEL SECURITY;

-- Least-privilege: el usuario solo LEE el log de sus clientes · toda la escritura
-- la hace el worker REX con service_role.
DROP POLICY IF EXISTS "rex_publish_log inherits clients RLS" ON rex_publish_log;
CREATE POLICY "rex_publish_log inherits clients RLS"
  ON rex_publish_log FOR SELECT
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

DROP POLICY IF EXISTS "Service role manages rex_publish_log" ON rex_publish_log;
CREATE POLICY "Service role manages rex_publish_log"
  ON rex_publish_log FOR ALL
  USING (auth.role() = 'service_role');

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SELECT manual en SQL Editor):
--   SELECT column_name FROM information_schema.columns
--     WHERE table_name='clients'
--     AND column_name IN ('rex_addon_active','autonomous_mode_on','crisis_active');
--   -- Esperado: 3 filas
--
--   SELECT table_name FROM information_schema.tables
--     WHERE table_schema='public' AND table_name='rex_publish_log';
--   -- Esperado: 1 fila
--
--   SELECT indexname FROM pg_indexes WHERE tablename='rex_publish_log';
--   -- Esperado: rex_publish_log_pkey · idx_rex_publish_log_client_time
--
--   SELECT count(*) FROM rex_publish_log;  -- Esperado: 0
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00069
-- ═══════════════════════════════════════════════════════════════════
