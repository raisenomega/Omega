-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00078 · RLS en apscheduler_jobs (B1 · 🔴 cierre exposición)║
-- ║  24 jun 2026 · cerrar lectura anon de la tabla del scheduler         ║
-- ║                                                                   ║
-- ║  CASO (sonda B1 · verificado en vivo): la tabla del jobstore         ║
-- ║  persistente (27 crons · rex_publisher/db_guardian/secrets_rotation… ║
-- ║  · job_state = paths de workers app.* + cron schedules) está         ║
-- ║  EXPUESTA vía PostgREST: la ANON key (pública) la lee (HTTP 200) =    ║
-- ║  info-disclosure de la arquitectura interna de workers.             ║
-- ║                                                                   ║
-- ║  FIX: ENABLE ROW LEVEL SECURITY · SIN policy · SIN FORCE.            ║
-- ║  El scheduler accede como OWNER `postgres` (conexión directa         ║
-- ║  SQLAlchemy · DATABASE_URL) → los owners BYPASEAN RLS → los 27 crons  ║
-- ║  siguen leyendo/escribiendo. anon/authenticated (PostgREST) sin      ║
-- ║  policy → 0 filas. + REVOKE defensa-en-profundidad (riesgo           ║
-- ║  estructural: un job futuro con args sensibles no se filtraría).     ║
-- ║                                                                   ║
-- ║  ⚠️ NUNCA `FORCE ROW LEVEL SECURITY`: haría que el owner también     ║
-- ║  respete RLS → scheduler BLOQUEADO → 27 crons caídos.               ║
-- ║                                                                   ║
-- ║  DRY-RUN transaccional (savepoint + ROLLBACK · 24 jun) CONFIRMÓ:     ║
-- ║  tras ENABLE RLS → owner lee 27 · anon lee 0 · force=False.          ║
-- ║  Idempotente (ENABLE/REVOKE re-corribles sin error).                ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── Cerrar la exposición: RLS sin policy (anon/authenticated → 0 filas) ───
ALTER TABLE public.apscheduler_jobs ENABLE ROW LEVEL SECURITY;
-- (NO se crea ninguna policy a propósito · el scheduler entra como owner y bypasea RLS)

-- ─── Defensa en profundidad: quitar el privilegio de lectura a los roles públicos ───
-- (el owner postgres conserva todo · service_role intacto · solo se cierra el canal PostgREST)
REVOKE SELECT ON public.apscheduler_jobs FROM anon, authenticated;

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (manual · NO ejecuta acá):
--   -- RLS on, FORCE off (crítico que force=false):
--   SELECT relrowsecurity, relforcerowsecurity
--   FROM pg_class WHERE oid='public.apscheduler_jobs'::regclass;   -- esperado: t , f
--   -- Owner sigue leyendo los 27 jobs:
--   SELECT count(*) FROM public.apscheduler_jobs;                  -- esperado: 27
--   -- anon ya NO lee (vía PostgREST con la anon key): GET /rest/v1/apscheduler_jobs → 0/401
--   -- Crons vivos: revisar logs del scheduler tras el deploy (los 27 jobs siguen disparando).
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00078
