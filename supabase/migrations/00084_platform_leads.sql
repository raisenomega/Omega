-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00084 · platform_leads                                 ║
-- ║  02 jul 2026 · Landing OMEGA · leads de PLATAFORMA (no de reseller) ║
-- ║                                                                   ║
-- ║  Prepara la tabla `leads` para captar prospectos DIRECTO de OMEGA  ║
-- ║  (PYMEs y resellers) desde una landing de marca, sin pertenecer a  ║
-- ║  ningún reseller. 4 operaciones (aditivas · 0 filas existentes):   ║
-- ║   1) Arregla el write path roto: agrega message + contacted_at     ║
-- ║      (el código ya los escribe: leads.py/public.py + mixin).       ║
-- ║   2) reseller_id pasa a NULLABLE → leads de plataforma sin reseller.║
-- ║   3) audience (pyme|reseller) → qué quiere ser el lead de la landing.║
-- ║   4) RLS: leads de plataforma (reseller_id NULL) SOLO los ve el      ║
-- ║      super_owner (is_super_owner singleton · 00040). Los leads con   ║
-- ║      reseller_id conservan la policy existente (white-label).        ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- 1) Arreglar el write path roto (Camino A · aditivo · el código ya escribe estas columnas).
ALTER TABLE leads ADD COLUMN IF NOT EXISTS message text;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS contacted_at timestamptz;

-- 2) Permitir leads de plataforma OMEGA (sin reseller). La FK a resellers(id) ON DELETE
--    CASCADE se mantiene (un FK nullable es válido). 0 filas existentes → nada que migrar.
ALTER TABLE leads ALTER COLUMN reseller_id DROP NOT NULL;

-- 3) Distinguir qué quiere ser el lead de la landing (nullable · los por-reseller no lo usan).
ALTER TABLE leads ADD COLUMN IF NOT EXISTS audience text
  CHECK (audience IS NULL OR audience IN ('pyme','reseller'));

-- 4) RLS de plataforma (Llave 2 = is_super_owner singleton · 00040). La policy existente
--    "Leads inherit reseller RLS" (reseller_id IN mis-resellers) se MANTIENE para leads con
--    reseller_id. Añadimos una policy para leads de plataforma (reseller_id IS NULL): solo el
--    super_owner los ve por acceso directo vía Supabase client (el backend usa service-role
--    que bypassa RLS · esta policy protege el camino frontend · defensa correcta, no redundante).
DROP POLICY IF EXISTS "Platform leads super_owner only" ON leads;
CREATE POLICY "Platform leads super_owner only"
  ON leads FOR ALL
  USING (
    reseller_id IS NULL
    AND EXISTS (
      SELECT 1 FROM resellers
      WHERE owner_user_id = auth.uid() AND is_super_owner = true
    )
  );
