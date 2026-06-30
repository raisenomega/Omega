-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00083 · strategy_idea_usages.archived_at               ║
-- ║  30 jun 2026 · REDISEÑO Estrategias Fase C.2 · archivar IDEA usada  ║
-- ║                                                                   ║
-- ║  ADITIVA: 1 columna nullable · no altera nada existente.          ║
-- ║  NULL = idea en "Usadas" · seteado = idea en "Archivadas".         ║
-- ║  Las idea-usages existentes quedan NULL (siguen en Usadas · honesto)║
-- ║  Hereda el RLS de strategy_idea_usages (00082 · no cambia).        ║
-- ║  use-idea / used-ideas siguen igual · el filtro archived = codigo. ║
-- ╚═══════════════════════════════════════════════════════════════════╝

ALTER TABLE strategy_idea_usages ADD COLUMN IF NOT EXISTS archived_at timestamptz;

COMMENT ON COLUMN strategy_idea_usages.archived_at IS
  'Archivado de idea usada. NULL = Usadas, seteado = Archivadas. Fase C.2.';
