-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00036 · agent_memory embedding 1536→1024 (DEBT-048)     ║
-- ║  27 may 2026 · ARIA attention-based memory via Voyage AI.          ║
-- ║                                                                   ║
-- ║  00002 creó embedding vector(1536) pensando en otro modelo, pero  ║
-- ║  la columna quedó SIEMPRE NULL: la memoria usaba Qdrant externo.   ║
-- ║  DEBT-048 trae embeddings nativos pgvector con voyage-3-large      ║
-- ║  (output_dimension=1024). Como la columna nunca tuvo datos, el     ║
-- ║  cambio de dimensión es seguro (USING NULL · no hay nada que       ║
-- ║  castear). Recreamos el índice ivfflat cosine y find_similar_      ║
-- ║  memories con el param a 1024 (mismo body/return que 00002).       ║
-- ║  Idempotente: DROP ... IF EXISTS antes de recrear · aditiva-fwd.   ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── 1. Soltar índice y función que dependen de vector(1536) ──────────
DROP INDEX IF EXISTS idx_agent_memory_embedding;
DROP FUNCTION IF EXISTS find_similar_memories(vector, text, uuid, integer, float);

-- ─── 2. Cambiar dimensión 1536→1024 · columna NULL/unused (seguro) ────
ALTER TABLE agent_memory ALTER COLUMN embedding TYPE vector(1024) USING NULL;

-- ─── 3. Recrear índice de similaridad (ivfflat, cosine distance) ──────
CREATE INDEX idx_agent_memory_embedding
  ON agent_memory USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- ─── 4. Recrear find_similar_memories con query_embedding 1024 ────────
CREATE OR REPLACE FUNCTION find_similar_memories(
  query_embedding vector(1024),
  target_agent_code text,
  target_client_id uuid DEFAULT NULL,
  limit_count integer DEFAULT 5,
  min_similarity float DEFAULT 0.7
)
RETURNS TABLE (
  id uuid,
  context text,
  decision text,
  reasoning text,
  was_correct boolean,
  confidence integer,
  similarity float
)
LANGUAGE sql
STABLE
AS $$
  SELECT
    m.id,
    m.context,
    m.decision,
    m.reasoning,
    m.was_correct,
    m.confidence,
    1 - (m.embedding <=> query_embedding) AS similarity
  FROM agent_memory m
  WHERE m.agent_code = target_agent_code
    AND (target_client_id IS NULL OR m.client_id = target_client_id)
    AND m.embedding IS NOT NULL
    AND 1 - (m.embedding <=> query_embedding) >= min_similarity
  ORDER BY m.embedding <=> query_embedding
  LIMIT limit_count;
$$;

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SQL Editor):
--   SELECT atttypmod FROM pg_attribute
--     WHERE attrelid = 'agent_memory'::regclass AND attname = 'embedding';  -- 1024
--   SELECT indexname FROM pg_indexes
--     WHERE tablename = 'agent_memory' AND indexname = 'idx_agent_memory_embedding';  -- 1 fila
--   SELECT pg_get_function_identity_arguments('find_similar_memories'::regproc);
--     -- vector(1024), text, uuid, integer, double precision
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00036
-- ═══════════════════════════════════════════════════════════════════
