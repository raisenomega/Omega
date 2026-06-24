-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00075 · reseller propio de raisen@ + "Mi negocio" Enterprise║
-- ║  24 jun 2026 · Commit 2/5 del flag cuenta-dueño                    ║
-- ║                                                                   ║
-- ║  raisen@ (84d86286) pasa a ser RESELLER PROPIO (como reseller@),    ║
-- ║  rex_live_enabled=TRUE, is_owner=FALSE (NO superadmin global).      ║
-- ║  REUSA su negocio cab55a38 "Mi negocio" (lo mueve al reseller nuevo  ║
-- ║  + lo promueve a Enterprise perpetuo) · NO crea negocio nuevo.      ║
-- ║  Paso 0 confirmó: mover = SOLO clients.reseller_id (cab55a38 sin     ║
-- ║  datos colgados · behavioral_events.reseller_id=NULL · resto 0).     ║
-- ║  Idempotente · aditiva. Ver SOURCE_OF_TRUTH §6.                     ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── 1 · Reseller propio de raisen@ (forma espejo de Test Reseller 894c202f) ───
-- Idempotente por slug (UNIQUE). is_owner/is_super_owner quedan en su DEFAULT false
-- (NO superadmin · raisen@ es reseller normal con flag owner_account, no admin global).
INSERT INTO resellers (owner_user_id, name, slug, plan, rex_live_enabled, aria_level, default_client_aria_level)
VALUES ('84d86286-e36e-4942-a312-0d65aab4bbe7', 'Raisen Omega', 'raisen-omega', 'enterprise', TRUE, 4, 4)
ON CONFLICT (slug) DO NOTHING;

-- ─── 2 · Mover "Mi negocio" (cab55a38) al reseller nuevo (SOLO reseller_id) ───
-- Referencia por slug (estable · funciona aunque el id sea gen_random_uuid).
UPDATE clients
SET reseller_id = (SELECT id FROM resellers WHERE slug = 'raisen-omega'),
    updated_at  = now()
WHERE id = 'cab55a38-2c1e-4c26-bbef-a1ad4e3337c6';

-- ─── 3 · Promover cab55a38 a Enterprise perpetuo (espejo de Zafacones afb9f578) ───
-- client_plans = fuente del gate (useClientPlanStatus lee client_plans.plan).
-- current_period_end perpetuo (cuenta dueño · sin expiración) · stripe_subscription_id queda NULL.
UPDATE client_plans
SET plan               = 'enterprise',
    current_period_end = '2099-12-31T00:00:00+00:00',
    updated_at         = now()
WHERE client_id = 'cab55a38-2c1e-4c26-bbef-a1ad4e3337c6';

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (manual · NO ejecuta acá):
--   SELECT id, slug, owner_user_id, rex_live_enabled, is_owner FROM resellers WHERE slug='raisen-omega';
--   SELECT id, name, reseller_id FROM clients WHERE id='cab55a38-2c1e-4c26-bbef-a1ad4e3337c6';  -- reseller_id = el nuevo
--   SELECT client_id, plan, current_period_end FROM client_plans WHERE client_id='cab55a38-2c1e-4c26-bbef-a1ad4e3337c6';  -- enterprise
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00075
