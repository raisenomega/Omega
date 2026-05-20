-- ═══════════════════════════════════════════════════════════════════
-- Migración 00010: behavioral_events soporta reseller_id
-- · Spec ARIA_NOVA_INTELLIGENCE §4.1: "EN AMBOS CASOS [cliente y reseller]
--   — siempre INSERT behavioral_events"
-- · Schema 00008 forzaba client_id NOT NULL · bloqueaba reseller signals
-- · Mantener client_id columna pero nullable · agregar reseller_id nullable
--   · chk_behavioral_owner_present garantiza al menos uno presente
-- ═══════════════════════════════════════════════════════════════════

-- 1. ALTER behavioral_events
ALTER TABLE behavioral_events
  ADD COLUMN IF NOT EXISTS reseller_id uuid REFERENCES resellers(id) ON DELETE CASCADE;

-- client_id deja de ser NOT NULL · solo se requiere uno de los dos
ALTER TABLE behavioral_events
  ALTER COLUMN client_id DROP NOT NULL;

-- chk_owner_present · matchea patrón agent_memory
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'chk_behavioral_owner_present'
  ) THEN
    ALTER TABLE behavioral_events
      ADD CONSTRAINT chk_behavioral_owner_present
      CHECK (client_id IS NOT NULL OR reseller_id IS NOT NULL);
  END IF;
END$$;

-- 2. Index reseller · partial (solo cuando reseller_id present)
CREATE INDEX IF NOT EXISTS idx_behavioral_events_reseller_created
  ON behavioral_events (reseller_id, created_at DESC)
  WHERE reseller_id IS NOT NULL;
