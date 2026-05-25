-- 00026_content_outcome_evaluated.sql (26 may 2026)
-- Habilita el cron outcome_evaluator (4A-2 · PASO 3 del ciclo de auto-aprendizaje).
-- Marca de idempotencia: cuándo se evaluó el outcome de un contenido a 72h.
-- Sin esta columna el cron re-procesaría los mismos drafts cada noche.
--
-- El positivo (contenido aprobado → was_correct=True) ya lo registra
-- insert_agent_memory_approved al guardar. Esta columna sostiene SOLO el negativo:
-- drafts abandonados >72h que el cron marca was_correct=False (proxy is_saved=status).
-- Idempotente · safe en re-runs (ADD COLUMN IF NOT EXISTS · CREATE INDEX IF NOT EXISTS).

ALTER TABLE content_lab_generated
  ADD COLUMN IF NOT EXISTS outcome_evaluated_at timestamptz;

-- Índice parcial: el cron solo escanea drafts sin evaluar (selectivo · barato).
CREATE INDEX IF NOT EXISTS idx_contentlab_outcome_pending
  ON content_lab_generated (created_at)
  WHERE status = 'draft' AND outcome_evaluated_at IS NULL;

COMMENT ON COLUMN content_lab_generated.outcome_evaluated_at IS
  'Timestamp en que outcome_evaluator registró el outcome a 72h (NULL = pendiente). Idempotencia del cron 4A-2.';
