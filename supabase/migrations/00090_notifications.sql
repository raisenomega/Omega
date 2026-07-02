-- ╔══════════════════════════════════════════════════════════════════════════════╗
-- ║  00090 · notifications (F6-corrección · pieza 3 · net-new)                       ║
-- ╚══════════════════════════════════════════════════════════════════════════════╝
-- Notificaciones in-app por usuario (destinatario = auth uid). El backend inserta con service-role
-- (bypass RLS); el usuario ve/actualiza SOLO las suyas (defensa · las lecturas van por endpoint
-- guardado igual). SIN policy de INSERT → anon/auth no pueden insertar (solo service-role).
CREATE TABLE IF NOT EXISTS notifications (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL,
  type        text NOT NULL DEFAULT 'lead',
  title       text NOT NULL,
  body        text,
  is_read     boolean NOT NULL DEFAULT false,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications (user_id, is_read);

ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "own notifications select" ON notifications;
CREATE POLICY "own notifications select" ON notifications
  FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "own notifications update" ON notifications;
CREATE POLICY "own notifications update" ON notifications
  FOR UPDATE USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);

-- Resolver email → user_id (pieza 3 · D-A) · el admin API list_users NO filtra por email server-side
-- (solo pagina) → esta función SECURITY DEFINER hace el lookup O(1) indexado, case-insensitive, sin
-- paginación. REVOKE de anon/authenticated → solo el backend (service-role) la llama (no expone
-- enumeración de usuarios al público).
CREATE OR REPLACE FUNCTION public.user_id_by_email(p_email text)
RETURNS uuid
LANGUAGE sql SECURITY DEFINER SET search_path = auth, public AS $$
  SELECT id FROM auth.users WHERE lower(email) = lower(p_email) LIMIT 1;
$$;
-- Postgres otorga EXECUTE a PUBLIC por defecto en toda función nueva → hay que revocar de PUBLIC
-- (revocar solo de anon/authenticated NO anula la herencia vía PUBLIC) · solo service-role la ejecuta.
REVOKE ALL ON FUNCTION public.user_id_by_email(text) FROM PUBLIC, anon, authenticated;
