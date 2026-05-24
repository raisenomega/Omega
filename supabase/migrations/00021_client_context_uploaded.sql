-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00021 · uploaded_context_text en client_context        ║
-- ║  24 may 2026 · Sprint 3 · DEBT-039 V2 close (persistent doc)      ║
-- ║                                                                    ║
-- ║  Permite subir UN documento .pdf/.docx/.md/.txt por cliente cuyo  ║
-- ║  texto extraído se inyecta SIEMPRE al system prompt de RAFA       ║
-- ║  (no per-request como DEBT-CL-020 attachment · este es persistent ║
-- ║  context · forma parte de la identidad del cliente para ARIA).    ║
-- ║                                                                    ║
-- ║  Re-upload sobrescribe · V1 sin history (1 doc por cliente).      ║
-- ║  Idempotente: ADD COLUMN IF NOT EXISTS · safe en re-runs.         ║
-- ╚═══════════════════════════════════════════════════════════════════╝

ALTER TABLE client_context
  ADD COLUMN IF NOT EXISTS uploaded_context_text text,
  ADD COLUMN IF NOT EXISTS uploaded_context_filename text,
  ADD COLUMN IF NOT EXISTS uploaded_context_mime text,
  ADD COLUMN IF NOT EXISTS uploaded_context_at timestamptz;

COMMENT ON COLUMN client_context.uploaded_context_text IS
  'Texto extraído de doc adjunto (PDF/DOCX/MD/TXT · cap 50K chars · vía _attachment_extractor). Inyectado al system prompt RAFA en cada generación.';
