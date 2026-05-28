-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00041 · signup trigger idempotente · cierra DEBT-099 bug║
-- ║  28 may 2026                                                       ║
-- ║                                                                   ║
-- ║  CONTEXTO · POST-MORTEM                                            ║
-- ║  ─────────────────────                                             ║
-- ║  00006 (12 may) creó trigger AFTER INSERT ON auth.users →          ║
-- ║    auto_provision_client_on_signup() que INSERTa clients + un      ║
-- ║    INSERT directo a client_plans (period 7d, Adopción §3).         ║
-- ║                                                                   ║
-- ║  00039 (27 may · DEBT-095) agregó AFTER INSERT ON clients →        ║
-- ║    provision_client_plan() que INSERTa client_plans (period 30d)   ║
-- ║    con ON CONFLICT DO NOTHING.                                     ║
-- ║                                                                   ║
-- ║  Cadena al firmar usuario:                                         ║
-- ║    auth.users INSERT → 00006 trig →                                ║
-- ║      INSERT clients → 00039 trig → INSERT client_plans OK (30d)    ║
-- ║      INSERT client_plans (7d, SIN ON CONFLICT) → UNIQUE VIOLATION  ║
-- ║      → rollback de toda la transacción → 500 al cliente            ║
-- ║      "Database error saving new user"                              ║
-- ║                                                                   ║
-- ║  FIX (Opción A · preserva spec §3 Adopción 7d)                     ║
-- ║  ──────────────────────────────────────────────                    ║
-- ║  CREATE OR REPLACE de la función vieja con UPSERT que pisa el      ║
-- ║  period dejado por el trigger nuevo (30d→7d) cuando el usuario     ║
-- ║  arranca en Adopción. Idempotente: si el INSERT a client_plans     ║
-- ║  ya existe (caso normal vía 00039), hace UPDATE de plan+period.    ║
-- ║                                                                   ║
-- ║  Confirmado vivo: el UniqueViolation reproducía 1:1 en dry-run     ║
-- ║  (tx revertida) antes de este fix.                                 ║
-- ║                                                                   ║
-- ║  Solo-aditiva sobre función pública. NO toca el trigger 00039      ║
-- ║  (sigue siendo válido como red para INSERTs a clients fuera del    ║
-- ║  flujo signup, ej. reseller crea cliente desde dashboard).         ║
-- ╚═══════════════════════════════════════════════════════════════════╝

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

  -- Reseller default "OMEGA Direct"
  SELECT id INTO default_reseller_id
  FROM resellers WHERE slug = 'omega-direct';

  IF default_reseller_id IS NULL THEN
    RAISE WARNING 'OMEGA Direct reseller not found · skip auto-provision for user %', NEW.id;
    RETURN NEW;
  END IF;

  -- Crear clients row (plan=adopcion, status=active)
  -- El INSERT dispara trg_provision_client_plan (00039) que ya inserta
  -- una fila en client_plans con period=30d como red de seguridad.
  INSERT INTO clients (user_id, reseller_id, name, plan, status)
  VALUES (NEW.id, default_reseller_id, 'Mi negocio', 'adopcion', 'active')
  RETURNING id INTO new_client_id;

  -- Pisar el period a 7d (spec §3 Adopción) vía UPSERT idempotente.
  -- ON CONFLICT (client_id) cubre el caso normal en el que el trigger
  -- 00039 ya insertó la fila con period=30d.
  INSERT INTO client_plans (client_id, plan, current_period_start, current_period_end)
  VALUES (new_client_id, 'adopcion', now(), now() + interval '7 days')
  ON CONFLICT (client_id) DO UPDATE
    SET plan                 = EXCLUDED.plan,
        current_period_start = EXCLUDED.current_period_start,
        current_period_end   = EXCLUDED.current_period_end;

  RETURN NEW;
END;
$$;

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (smoke test desde shell con service-role):
--   BEGIN;
--   INSERT INTO auth.users (instance_id, id, aud, role, email,
--                           encrypted_password, email_confirmed_at,
--                           raw_app_meta_data, raw_user_meta_data,
--                           created_at, updated_at)
--   VALUES ('00000000-0000-0000-0000-000000000000', gen_random_uuid(),
--           'authenticated','authenticated','smoke@diag.local',
--           crypt('x', gen_salt('bf')), now(), '{}'::jsonb, '{}'::jsonb,
--           now(), now());
--   -- Debe terminar sin error.
--   ROLLBACK;
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00041
