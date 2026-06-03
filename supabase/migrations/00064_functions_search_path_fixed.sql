-- 00064_functions_search_path_fixed.sql
-- Cierra 5 MEDIUM del Supabase Linter (function_search_path_mutable).
-- Fija search_path explícito → evita search_path hijacking. Hardening puro · cero cambio de comportamiento.
-- Signatures exactas verificadas vía pg_get_function_identity_arguments.

ALTER FUNCTION public.set_updated_at() SET search_path = public, pg_temp;
ALTER FUNCTION public.update_updated_at_column() SET search_path = public, pg_temp;
ALTER FUNCTION public.invalidate_brand_dna_on_corpus_change() SET search_path = public, pg_temp;
ALTER FUNCTION public.sentinel_endpoint_latency(integer) SET search_path = public, pg_temp;
ALTER FUNCTION public.find_similar_memories(vector, text, uuid, integer, double precision) SET search_path = public, pg_temp;

-- ═══════════════════════════════════════════════════════════════════
-- Verificación:  SELECT proname, proconfig FROM pg_proc WHERE proname IN
--   ('set_updated_at','update_updated_at_column','invalidate_brand_dna_on_corpus_change',
--    'sentinel_endpoint_latency','find_similar_memories');  -- esperado: proconfig con search_path
-- ═══════════════════════════════════════════════════════════════════
