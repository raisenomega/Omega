-- ═══════════════════════════════════════════════════════════════════
-- OmegaRaisen — Migración 00006: Auto-provisión clients + client_plans
-- · Cierre parcial DEBT-032 (parte trigger · Stripe webhook queda Fase 3)
-- · Cada auth.users INSERT → clients (Adopción 7d) + client_plans (now+7d)
-- · Guard contra reseller owners vía resellers.owner_user_id
-- · Backfill excluye Ibrain (owner) y reseller@omega.com (reseller pendiente
--   de configurar en tabla resellers — protección temporal por email)
-- ═══════════════════════════════════════════════════════════════════

-- ─── 1. Reseller default "OMEGA Direct" con Ibrain como owner ─────
-- Subquery resuelve el owner_user_id en tiempo de aplicación.
-- raisenagencypr@gmail.com debe existir en auth.users (verificado: SÍ).
-- Si no existiera, INSERT fallaría por NOT NULL en owner_user_id.
INSERT INTO resellers (slug, name, owner_user_id, status, plan)
VALUES (
  'omega-direct',
  'OMEGA Direct',
  (SELECT id FROM auth.users WHERE email = 'raisenagencypr@gmail.com' LIMIT 1),
  'active',
  'enterprise'
)
ON CONFLICT (slug) DO NOTHING;

-- ─── 2. Función de auto-provisión con guard ───────────────────────
-- SECURITY DEFINER necesario: el trigger corre en INSERT sobre auth.users
-- que ocurre antes que el user tenga sesión · necesita privilegios para
-- escribir en clients (RLS-protected).
CREATE OR REPLACE FUNCTION public.auto_provision_client_on_signup()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, auth
AS $$
DECLARE
  default_reseller_id uuid;
  is_reseller_owner   boolean;
  new_client_id       uuid;
BEGIN
  -- Guard 1: skip si el user ya es owner de algún reseller
  SELECT EXISTS(
    SELECT 1 FROM resellers WHERE owner_user_id = NEW.id
  ) INTO is_reseller_owner;

  IF is_reseller_owner THEN
    RETURN NEW;
  END IF;

  -- Obtener reseller default
  SELECT id INTO default_reseller_id
  FROM resellers WHERE slug = 'omega-direct';

  IF default_reseller_id IS NULL THEN
    RAISE WARNING 'OMEGA Direct reseller not found · skip auto-provision for user %', NEW.id;
    RETURN NEW;
  END IF;

  -- Crear clients row (plan=adopcion, status=active)
  INSERT INTO clients (user_id, reseller_id, name, plan, status)
  VALUES (NEW.id, default_reseller_id, 'Mi negocio', 'adopcion', 'active')
  RETURNING id INTO new_client_id;

  -- Crear client_plans row con período 7 días (spec §3 Adopción)
  INSERT INTO client_plans (client_id, plan, current_period_start, current_period_end)
  VALUES (new_client_id, 'adopcion', now(), now() + interval '7 days');

  RETURN NEW;
END;
$$;

-- ─── 3. Trigger AFTER INSERT en auth.users ────────────────────────
DROP TRIGGER IF EXISTS on_auth_user_created_provision_client ON auth.users;
CREATE TRIGGER on_auth_user_created_provision_client
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.auto_provision_client_on_signup();

-- ─── 4. Backfill: solo cliente@omega.com debe recibir clients+plan ─
-- Exclusiones explícitas por email:
--   · raisenagencypr@gmail.com → owner de omega-direct (Guard 1 lo cubre)
--   · reseller@omega.com       → reseller demo pendiente de configurar
--     en tabla resellers. Cuando se le asigne owner_user_id en una
--     fila resellers, el Guard 1 lo cubrirá automáticamente y este
--     filtro por email puede removerse.
DO $$
DECLARE
  u record;
  default_reseller_id uuid;
  new_client_id uuid;
BEGIN
  SELECT id INTO default_reseller_id FROM resellers WHERE slug = 'omega-direct';

  IF default_reseller_id IS NULL THEN
    RAISE EXCEPTION 'OMEGA Direct reseller not found · backfill aborted';
  END IF;

  FOR u IN
    SELECT au.id, au.email
    FROM auth.users au
    WHERE NOT EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = au.id)
      AND NOT EXISTS (SELECT 1 FROM clients   WHERE user_id       = au.id)
      AND au.email NOT IN (
        'raisenagencypr@gmail.com',
        'reseller@omega.com'
      )
  LOOP
    INSERT INTO clients (user_id, reseller_id, name, plan, status)
    VALUES (u.id, default_reseller_id, 'Mi negocio', 'adopcion', 'active')
    RETURNING id INTO new_client_id;

    INSERT INTO client_plans (client_id, plan, current_period_start, current_period_end)
    VALUES (new_client_id, 'adopcion', now(), now() + interval '7 days');

    RAISE NOTICE 'Backfilled client+plan for user %', u.email;
  END LOOP;
END$$;
