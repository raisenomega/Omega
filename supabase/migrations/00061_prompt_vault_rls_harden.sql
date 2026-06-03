-- 00061_prompt_vault_rls_harden.sql
-- Cierra el HIGH PERMISSIVE_TRUE + MEDIUM ASYMMETRIC de Capa 6 sobre prompt_vault.
-- prompt_vault = tabla SISTEMA global (36 prompts RAFA · sin tenant · IP de prompt-engineering).
-- La policy `authenticated USING(true)` (00014) exponía los prompts a CUALQUIER user logueado vía
-- Supabase directo. Backend lee/escribe con service_role (bypassa RLS) · frontend NO accede directo
-- → service_role-only es seguro y cero-impacto funcional. Aditiva (DROP IF EXISTS + CREATE).

DROP POLICY IF EXISTS prompt_vault_read_authenticated ON prompt_vault;
DROP POLICY IF EXISTS "prompt_vault_service_role_all" ON prompt_vault;

CREATE POLICY "prompt_vault_service_role_all"
  ON prompt_vault
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply:  SELECT public.sentinel_rls_audit() -> 'issues';
--   -- esperado: sin filas de prompt_vault (ni PERMISSIVE_TRUE ni ASYMMETRIC_POLICIES)
-- ═══════════════════════════════════════════════════════════════════
