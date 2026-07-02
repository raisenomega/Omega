-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║  00089 · leads CRM (F6-corrección · réplica AdminLeads del molde)                ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
-- Campos que la tabla `leads` no tenía y el CRM del molde usa (todos nullable · aditivos ·
-- idempotentes · la landing no los captura hoy → se llenan por edición del owner en /web/leads):
--   · temperature  — temperatura CRM (D1 · CHECK frio|tibio|caliente|convertido)
--   · company      — empresa (D2 · buscador + editar; budget/website NO se añaden: eran de Raisen)
--   · whatsapp_username — click-to-chat wa.me (D6 · prep DEBT-WA-DUAL-IDENTITY-READINESS)
-- La RLS de leads (00001 reseller + 00084 super_owner) ya protege · escritura solo por endpoints
-- guardados (checkpoint A F6) · el CRM nunca escribe Supabase directo.

ALTER TABLE leads
  ADD COLUMN IF NOT EXISTS temperature       text,
  ADD COLUMN IF NOT EXISTS company           text,
  ADD COLUMN IF NOT EXISTS whatsapp_username text;

-- CHECK de temperature (nullable) · drop-then-add = idempotente.
ALTER TABLE leads DROP CONSTRAINT IF EXISTS leads_temperature_check;
ALTER TABLE leads ADD CONSTRAINT leads_temperature_check
  CHECK (temperature IS NULL OR temperature IN ('frio', 'tibio', 'caliente', 'convertido'));
