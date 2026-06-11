-- ═══════════════════════════════════════════════════════════════════
-- 00067_content_brand_voice_scored_at.sql
-- P0-2 (auditoría externa 10 jun 2026) · gate X5 brand voice con cache.
-- Aditiva y segura: 1 columna nullable + 1 función. La columna del SCORE
-- (brand_voice_score numeric(3,2)) YA existe desde 00001 · solo faltaba el
-- timestamp del scoring para el stale-check del cache (refinamiento 1).
-- ═══════════════════════════════════════════════════════════════════

ALTER TABLE content_lab_generated
  ADD COLUMN IF NOT EXISTS brand_voice_scored_at timestamptz;

ALTER TABLE content_lab_generated
  ADD COLUMN IF NOT EXISTS brand_voice_score numeric(3,2);  -- defensivo · ya existe en 00001

-- Persistencia atómica del score: setea score + scored_at=now() en UNA
-- transacción. now() es estable por transacción → scored_at == el updated_at
-- que el trigger set_updated_at (00001) pone en el MISMO UPDATE. Así el
-- stale-check (scored_at >= updated_at) da TRUE recién escrito (cache hit) y
-- solo se invalida cuando una EDICIÓN posterior mueve updated_at hacia adelante.
CREATE OR REPLACE FUNCTION mark_brand_voice_scored(p_content_id uuid, p_score numeric)
RETURNS void
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
  UPDATE content_lab_generated
     SET brand_voice_score = p_score,
         brand_voice_scored_at = now()
   WHERE id = p_content_id;
$$;

REVOKE ALL ON FUNCTION mark_brand_voice_scored(uuid, numeric) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION mark_brand_voice_scored(uuid, numeric) TO service_role;
