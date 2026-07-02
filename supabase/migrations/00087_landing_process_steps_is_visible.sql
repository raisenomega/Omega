-- ╔══════════════════════════════════════════════════════════════════════════╗
-- ║  00087 · landing_process_steps gana is_visible (visibilidad por-paso)       ║
-- ╚══════════════════════════════════════════════════════════════════════════╝
-- Rebanada 3 (Proceso). Mismo patrón que 00086 (servicios): visibilidad POR PASO para poder
-- apagar un paso sin borrar su contenido bilingüe (el molde solo oculta a nivel de sección).
-- Additiva e idempotente · DEFAULT true → los 4 pasos sembrados quedan visibles · la RLS
-- super_owner ya existente (00085) protege el UPDATE.
ALTER TABLE landing_process_steps
  ADD COLUMN IF NOT EXISTS is_visible boolean NOT NULL DEFAULT true;
