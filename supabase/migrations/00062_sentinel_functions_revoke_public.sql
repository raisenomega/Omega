-- 00062_sentinel_functions_revoke_public.sql
-- Cierra 3 CRITICAL del Supabase Linter (anon/authenticated_security_definer_function_executable).
-- Las funciones SENTINEL son herramientas internas SECURITY DEFINER · solo service_role debe ejecutarlas.
-- Verificado: TODOS los callers backend usan get_supabase_service() (service_role) → cero impacto.
-- service_role conserva su GRANT explícito (00052/00055/00059) · esto solo quita el default PUBLIC.

REVOKE EXECUTE ON FUNCTION public.sentinel_rls_audit() FROM anon, authenticated, PUBLIC;
REVOKE EXECUTE ON FUNCTION public.sentinel_slow_queries(integer, integer) FROM anon, authenticated, PUBLIC;
REVOKE EXECUTE ON FUNCTION public.sentinel_webhook_idempotency_enforced() FROM anon, authenticated, PUBLIC;

-- ═══════════════════════════════════════════════════════════════════
-- Verificación:  SELECT proacl FROM pg_proc WHERE proname='sentinel_rls_audit';
--   -- esperado: sin anon=X ni authenticated=X · solo postgres + service_role
-- ═══════════════════════════════════════════════════════════════════
