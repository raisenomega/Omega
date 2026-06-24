-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00076 · backfill cuentas-dueño → Enterprise en AMBAS columnas║
-- ║  24 jun 2026 · A2.1 · restaurar invariante clients.plan==client_plans.plan║
-- ║                                                                   ║
-- ║  Los negocios ACTUALES de las cuentas-dueño (owner_accounts · 00074) ║
-- ║  quedaron en 'basic'. Nuestro Commit 4 (promote) escribía SOLO       ║
-- ║  client_plans → invariante roto. A2.1 corrige promote (ambas cols) y  ║
-- ║  esta migración backfillea los negocios ya existentes.              ║
-- ║                                                                   ║
-- ║  Espejo de on_checkout_completed (webhook real escribe AMBAS cols).  ║
-- ║  WHERE derivado de owner_accounts + clients.user_id (NO hardcode de  ║
-- ║  ids · cubre todos los actuales y futuros backfills). SOLO toca      ║
-- ║  negocios de cuentas-dueño · NINGUNO de cuenta normal.             ║
-- ║  Idempotente · aditiva · re-corrible (guards IS DISTINCT FROM).      ║
-- ║  Enterprise perpetuo (2099) · NO setea current_period_start (la      ║
-- ║  convención perpetua de 00075/cliente@ no lo gestiona). NO toca      ║
-- ║  ownership (user_id/reseller_id) · exime de PAGO, nunca aislamiento. ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── 1 · clients.plan → enterprise (solo negocios de cuentas-dueño) ───
UPDATE clients
SET plan       = 'enterprise',
    updated_at = now()
WHERE user_id IN (SELECT user_id FROM owner_accounts)
  AND plan IS DISTINCT FROM 'enterprise';

-- ─── 2 · client_plans.plan → enterprise perpetuo (mismos negocios) ───
-- Restaura el invariante: la misma columna 'plan' que clients, fuente del gate.
UPDATE client_plans
SET plan               = 'enterprise',
    current_period_end = '2099-12-31T00:00:00+00:00',
    updated_at         = now()
WHERE client_id IN (
        SELECT c.id FROM clients c
        WHERE c.user_id IN (SELECT user_id FROM owner_accounts)
      )
  AND (plan IS DISTINCT FROM 'enterprise'
       OR current_period_end IS DISTINCT FROM '2099-12-31T00:00:00+00:00'::timestamptz);

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (manual · NO ejecuta acá):
--   -- Ambas columnas enterprise para TODOS los negocios de cuentas-dueño:
--   SELECT c.id, c.name, c.plan AS clients_plan, cp.plan AS client_plans_plan, cp.current_period_end
--   FROM clients c
--   JOIN client_plans cp ON cp.client_id = c.id
--   WHERE c.user_id IN (SELECT user_id FROM owner_accounts)
--   ORDER BY c.name;
--   -- Esperado: clients_plan = client_plans_plan = 'enterprise' · current_period_end = 2099-12-31 · 5 filas
--
--   -- Anti-fuga: NINGÚN negocio de cuenta normal pasó a enterprise por esta migración
--   -- (control · cuenta el universo enterprise fuera de owner_accounts antes/después debe ser igual).
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00076
