-- ═══════════════════════════════════════════════════════════════════
-- Migración 00014 · prompt_vault
-- Tabla canónica de los 30 prompts del Content Lab (RAFA copywriter).
-- Spec: CONTENT_LAB_OMEGA_MASTER.md §5
-- Reglas: G3 (RLS obligatoria) · A1 (DDD · tabla compartida sin tenant)
-- ═══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS prompt_vault (
  id                uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  category          text        NOT NULL,
  vertical          text        NOT NULL,
  platform          text        NOT NULL,
  agent_code        text        NOT NULL DEFAULT 'RAFA',
  performance_score numeric(3,1),
  prompt_text       text        NOT NULL,
  version           integer     NOT NULL DEFAULT 1,
  is_active         boolean     NOT NULL DEFAULT true,
  times_used        integer     NOT NULL DEFAULT 0,
  engagement_avg    numeric(4,2),
  created_at        timestamptz NOT NULL DEFAULT now(),
  updated_at        timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT prompt_vault_slot_unique UNIQUE (category, vertical, platform, version)
);

CREATE INDEX IF NOT EXISTS idx_prompt_vault_lookup
  ON prompt_vault (vertical, platform, category, is_active);

ALTER TABLE prompt_vault ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS prompt_vault_read_authenticated ON prompt_vault;
CREATE POLICY prompt_vault_read_authenticated
  ON prompt_vault
  FOR SELECT
  TO authenticated
  USING (true);

COMMENT ON TABLE prompt_vault IS
  'Prompts canónicos por (category, vertical, platform). Seedeados via scripts/seed_prompt_vault.py · spec CONTENT_LAB_OMEGA_MASTER.md §5. Escritura solo via service_role (bypass RLS). Lectura: authenticated.';
