-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00038 · backfill client_plans para clientes sin fila    ║
-- ║  27 may 2026 · cierra el caveat de FIX 1/2/3                       ║
-- ║                                                                   ║
-- ║  Los clientes creados DESPUÉS de 00005 NO obtienen fila           ║
-- ║  client_plans (no hay trigger ni lógica de app que la cree) →     ║
-- ║  los handlers de activación post-pago hacen .update().eq(client)  ║
-- ║  y encuentran 0 filas → el addon comprado NO se persiste · además ║
-- ║  el demo veía client_plans_missing. Re-corre el backfill de 00005 ║
-- ║  (mismo patrón · ON CONFLICT DO NOTHING) · idempotente · solo      ║
-- ║  inserta lo que falta (cero UPDATE/DROP · no toca filas existentes)║
-- ║                                                                   ║
-- ║  FOLLOW-UP: crear la fila client_plans al crear el cliente        ║
-- ║  (trigger AFTER INSERT en clients, o en el alta de la app) para   ║
-- ║  cerrar el gap a futuro · ver DEBT (registrar).                   ║
-- ╚═══════════════════════════════════════════════════════════════════╝

INSERT INTO client_plans (client_id, plan, current_period_start, current_period_end)
SELECT id,
       CASE
         WHEN plan IN ('adopcion','basic','pro','enterprise') THEN plan
         ELSE 'basic'
       END,
       created_at,
       created_at + interval '30 days'
FROM clients
ON CONFLICT (client_id) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (SQL Editor):
--   SELECT COUNT(*) FROM clients c
--     LEFT JOIN client_plans p ON p.client_id = c.id
--     WHERE p.client_id IS NULL;   -- Esperado: 0 (ningún cliente sin fila)
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00038
