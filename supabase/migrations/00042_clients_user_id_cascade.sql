-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00042 · clients.user_id ON DELETE CASCADE              ║
-- ║  28 may 2026 · cleanup DEBT-099 · desbloquea borrar users dashboard║
-- ║                                                                   ║
-- ║  CONTEXTO · POST-MORTEM                                            ║
-- ║  ─────────────────────                                             ║
-- ║  La FK `public.clients.user_id → auth.users(id)` se creó en 00001 ║
-- ║  con `NO ACTION` (default cuando no se especifica nada).          ║
-- ║                                                                   ║
-- ║  Como el trigger 00006 `auto_provision_client_on_signup` crea     ║
-- ║  una fila en `clients` por cada signup, TODO user firmado tiene  ║
-- ║  al menos una fila de `clients` referenciándolo → DELETE auth.    ║
-- ║  users levanta ForeignKeyViolation → dashboard reporta            ║
-- ║  "Database error deleting user" (500).                            ║
-- ║                                                                   ║
-- ║  Confirmado vivo en dry-run read-only (savepoint con INSERT user ║
-- ║  + DELETE) antes de este fix:                                     ║
-- ║    ERROR: update or delete on table "users" violates foreign key ║
-- ║    constraint "clients_user_id_fkey" on table "clients"          ║
-- ║                                                                   ║
-- ║  FIX                                                              ║
-- ║  ───                                                              ║
-- ║  Recrear el FK con ON DELETE CASCADE. Al borrar un user:          ║
-- ║    auth.users DELETE → cascade a public.clients                   ║
-- ║                       → cascade a 30+ tablas hijas con CASCADE    ║
-- ║                         (client_plans, brand_files, etc.)         ║
-- ║                       → SET NULL en tablas de logs (agent_log,    ║
-- ║                         aria_conversations, etc.) preservando     ║
-- ║                         historial sin referencias colgadas.       ║
-- ║                                                                   ║
-- ║  La operación es atómica (DROP + ADD en una sola ALTER).          ║
-- ║  Reversible: re-aplicar con `NO ACTION` si fuera necesario.       ║
-- ╚═══════════════════════════════════════════════════════════════════╝

ALTER TABLE public.clients
  DROP CONSTRAINT clients_user_id_fkey,
  ADD CONSTRAINT clients_user_id_fkey
    FOREIGN KEY (user_id)
    REFERENCES auth.users(id)
    ON DELETE CASCADE;

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply:
--   SELECT confdeltype FROM pg_constraint WHERE conname='clients_user_id_fkey';
--   → 'c' (CASCADE). Antes era 'a' (NO ACTION).
--
-- Smoke test:
--   BEGIN;
--   INSERT INTO auth.users (...) VALUES (...) RETURNING id;  -- crea user fresh
--   DELETE FROM auth.users WHERE id=<uid>;                   -- debe pasar
--   ROLLBACK;
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00042
