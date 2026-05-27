-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00040 · is_super_owner (Security Dev · solo Ibrain)    ║
-- ║  27 may 2026 · DEBT-106 pre-req · acceso más estricto que is_owner║
-- ╚═══════════════════════════════════════════════════════════════════╝

ALTER TABLE resellers
  ADD COLUMN IF NOT EXISTS is_super_owner boolean NOT NULL DEFAULT false;

COMMENT ON COLUMN resellers.is_super_owner IS
  'TRUE solo para el operador principal de OMEGA (Ibrain Raisen). '
  'Garantía: partial unique index impide > 1 super_owner.';

CREATE UNIQUE INDEX IF NOT EXISTS uq_resellers_super_owner_singleton
  ON resellers (is_super_owner)
  WHERE is_super_owner = true;

-- Backfill Ibrain. NOTA (corrección vs spec original): owner_user_id NO es único
-- (migración 00023 · un user puede poseer varios resellers). Un UPDATE por
-- owner_user_id marcaría TODAS sus filas → violaría el singleton index → abort.
-- Por eso se limita a UNA fila determinística (la primera por created_at).
UPDATE resellers
SET is_super_owner = true
WHERE id = (
  SELECT r.id
  FROM resellers r
  JOIN auth.users u ON u.id = r.owner_user_id
  WHERE u.email = 'raisenagencypr@gmail.com'
  ORDER BY r.created_at, r.id
  LIMIT 1
);

-- Verificación post-apply:
--   SELECT name, is_owner, is_super_owner FROM resellers;
--   Esperado: 1 fila con is_super_owner=true
