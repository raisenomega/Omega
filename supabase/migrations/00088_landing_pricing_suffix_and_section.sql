-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║  00088 · Precios (Rebanada 4): price_suffix editable en add-ons + sección       ║
-- ║           'pricing' registrable en landing_sections                             ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
-- (1) price_suffix: los Video Packs se cobran mensual → el sufijo del precio ("/mes") NO se
--     hardcodea (regla del arco: TODO editable desde el superadmin). Columna additiva editable.
-- (2) La sección 'pricing' no estaba en el seed de 00085 (hero/services/process/lead_form + 2 off)
--     → se registra para que el owner pueda apagarla/prenderla como las demás (isVisible('pricing')).
-- Additiva e idempotente · la RLS super_owner ya existente (00085) protege el UPDATE.

ALTER TABLE landing_pricing_addons
  ADD COLUMN IF NOT EXISTS price_suffix text NOT NULL DEFAULT '/mes';

INSERT INTO landing_sections (name, is_visible, display_order)
VALUES ('pricing', true, 6)
ON CONFLICT (name) DO NOTHING;
