-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00030 · revoke_agent_stats                            ║
-- ║  26 may 2026 · DEBT-078 · seguridad / least-privilege            ║
-- ║                                                                   ║
-- ║  Qué: revoca SELECT sobre la vista agent_performance_stats a los  ║
-- ║   roles de cliente (authenticated · anon).                       ║
-- ║                                                                   ║
-- ║  Por qué: 00002:179 hace GRANT SELECT ... TO authenticated, así   ║
-- ║   cualquier usuario autenticado podía leer telemetría agregada    ║
-- ║   de los agentes (Supabase la marcaba "Unrestricted"). Es         ║
-- ║   telemetría interna · solo service_role/superadmin · el cliente  ║
-- ║   no debe verla.                                                  ║
-- ║                                                                   ║
-- ║  service_role NO se toca: el backend la sigue necesitando.        ║
-- ║  No se DROP/recrea la vista · solo se revocan privilegios         ║
-- ║   (cambio mínimo y seguro · aditiva en intención).                ║
-- ║  Idempotente: REVOKE de un privilegio inexistente es no-op en     ║
-- ║   Postgres (no genera error).                                     ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── DEBT-078 · least-privilege sobre telemetría interna ─────────────
-- agent_performance_stats es telemetría interna · solo service_role/superadmin ·
-- el cliente no debe verla. Revocamos el acceso de lectura a los roles de cliente.

REVOKE SELECT ON agent_performance_stats FROM authenticated;

-- Defensivo: si alguna concesión llegó a anon (vía default privileges), también se revoca.
-- No-op seguro si nunca tuvo el privilegio.
REVOKE SELECT ON agent_performance_stats FROM anon;

-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00030
-- ═══════════════════════════════════════════════════════════════════
