-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00039 · trigger auto-provisión client_plans            ║
-- ║  27 may 2026 · cierra el gap a futuro (00038 backfilleó los actuales)║
-- ║                                                                   ║
-- ║  AFTER INSERT ON clients → crea la fila client_plans del cliente  ║
-- ║  nuevo automáticamente. plan = el del cliente (NEW.plan · fallback ║
-- ║  'basic' si NULL/inválido · evita mismatch clients↔client_plans   ║
-- ║  para clientes 'adopcion'/trial). period = now()..+30d · addons []║
-- ║  · stripe_subscription_id NULL (default).                         ║
-- ║                                                                   ║
-- ║  SECURITY DEFINER + search_path fijo: un reseller/owner que crea  ║
-- ║  el cliente NO tiene INSERT directo en client_plans (RLS) → el    ║
-- ║  trigger debe bypassear RLS para no romper el alta del cliente.   ║
-- ║  Solo-aditiva · ON CONFLICT DO NOTHING · no toca filas existentes.║
-- ╚═══════════════════════════════════════════════════════════════════╝

CREATE OR REPLACE FUNCTION public.provision_client_plan()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
  INSERT INTO public.client_plans (
    client_id, plan, current_period_start, current_period_end, addons, stripe_subscription_id
  )
  VALUES (
    NEW.id,
    CASE WHEN NEW.plan IN ('adopcion','basic','pro','enterprise') THEN NEW.plan ELSE 'basic' END,
    now(),
    now() + interval '30 days',
    '[]'::jsonb,
    NULL
  )
  ON CONFLICT (client_id) DO NOTHING;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_provision_client_plan ON public.clients;
CREATE TRIGGER trg_provision_client_plan
  AFTER INSERT ON public.clients
  FOR EACH ROW
  EXECUTE FUNCTION public.provision_client_plan();

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply: crear un cliente de prueba → debe aparecer
-- su fila en client_plans automáticamente (plan = el del cliente).
--   SELECT tgname FROM pg_trigger WHERE tgrelid = 'public.clients'::regclass
--     AND tgname = 'trg_provision_client_plan';   -- 1 fila
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00039
