-- ╔════════════════════════════════════════════════════════════════════╗
-- ║  00086 · landing_services gana is_visible (visibilidad por-servicio)  ║
-- ╚════════════════════════════════════════════════════════════════════╝
-- Rebanada 2 (Servicios). El molde solo oculta servicios a nivel de sección; OMEGA gana
-- visibilidad POR TARJETA (mismo modelo que landing_sections) para poder apagar un servicio
-- sin borrar su contenido bilingüe. Additiva e idempotente · DEFAULT true → los 4 servicios
-- sembrados quedan visibles · la RLS super_owner ya existente (00085) protege el UPDATE.
ALTER TABLE landing_services
  ADD COLUMN IF NOT EXISTS is_visible boolean NOT NULL DEFAULT true;
