-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00023 · índice resellers.owner_user_id                 ║
-- ║  25 may 2026 · perf · guardian rec #1 (post role-derivation)      ║
-- ║                                                                    ║
-- ║  get_current_user deriva el rol server-side consultando           ║
-- ║  `resellers WHERE owner_user_id = <uid>` en CADA request          ║
-- ║  autenticado (forgery-proof · commit 33166e4). Sin índice =       ║
-- ║  seq scan por request. owner_user_id NO es único (un user puede   ║
-- ║  poseer múltiples resellers) → índice no-único.                   ║
-- ║                                                                    ║
-- ║  Aditiva · idempotente · cero cambios destructivos.               ║
-- ╚═══════════════════════════════════════════════════════════════════╝

CREATE INDEX IF NOT EXISTS idx_resellers_owner_user
  ON resellers(owner_user_id);
