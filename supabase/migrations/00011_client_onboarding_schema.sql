-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00011 · Client onboarding schema (DEBT-033 mayor)      ║
-- ║  20 may 2026 · Wizard Nuevo Cliente V3                            ║
-- ║                                                                   ║
-- ║  Cambios:                                                         ║
-- ║   §1 CREATE TABLE client_context           (30 cols)              ║
-- ║   §2 ALTER  TABLE social_accounts ADD 11 cols (OAuth Fase 2 ready)║
-- ║   §3 ALTER  TABLE brand_files ADD 3 cols (mime/category/url)      ║
-- ║   §4 CREATE TABLE client_brand_assets     (colors + fonts + FKs)  ║
-- ║   §5 ALTER  TABLE brand_voice_corpus · índice (client_id, ts)     ║
-- ║   §6 Helper set_updated_at() (idempotente)                        ║
-- ║                                                                   ║
-- ║  RLS habilitada en todas las tablas nuevas (G5).                  ║
-- ║  Aditiva: cero DROP · cero modificaciones destructivas.           ║
-- ║  Cierre parcial DEBT-031 (client_context referenciado por         ║
-- ║  analytics handler ahora existe).                                 ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── §6 · Helper set_updated_at (idempotente) ─────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ─── §1 · client_context (perfil rico del negocio · sec 2-8 wizard) ──
CREATE TABLE IF NOT EXISTS client_context (
  id                              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id                       uuid NOT NULL UNIQUE REFERENCES clients(id) ON DELETE CASCADE,
  niche                           text,
  vertical                        text,
  tone                            text,
  brand_voice                     jsonb NOT NULL DEFAULT '{}'::jsonb,
  business_what                   text,
  business_to_whom                text,
  business_diff                   text,
  business_size                   text,
  years_operating                 integer CHECK (years_operating IS NULL OR years_operating >= 0),
  target_audience                 text,
  audience_age_range              text,
  audience_gender                 text,
  competitors                     jsonb NOT NULL DEFAULT '[]'::jsonb,
  avoided_topics                  text,
  avoided_words                   jsonb NOT NULL DEFAULT '[]'::jsonb,
  preferred_formats               jsonb NOT NULL DEFAULT '[]'::jsonb,
  emoji_usage                     text,
  hashtag_strategy                text,
  primary_goal                    text,
  goal_this_month                 text,
  goal_this_quarter               text,
  goal_priority_now               text,
  success_metric                  text,
  monthly_revenue_target          numeric(12,2),
  has_existing_content            boolean NOT NULL DEFAULT false,
  existing_followers              integer CHECK (existing_followers IS NULL OR existing_followers >= 0),
  best_post_url                   text,
  what_worked                     text,
  what_failed                     text,
  content_themes                  jsonb NOT NULL DEFAULT '[]'::jsonb,
  custom_instructions             text,
  emergency_contact_name          text,
  emergency_contact_phone         text,
  requires_publish_approval       boolean NOT NULL DEFAULT true,
  preferred_publishing_hours      jsonb NOT NULL DEFAULT '[]'::jsonb,
  timezone                        text NOT NULL DEFAULT 'America/Puerto_Rico',
  onboarding_complete             boolean NOT NULL DEFAULT false,
  onboarding_completion_percent   integer NOT NULL DEFAULT 0 CHECK (onboarding_completion_percent BETWEEN 0 AND 100),
  onboarded_at                    timestamptz,
  created_at                      timestamptz NOT NULL DEFAULT now(),
  updated_at                      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_client_context_client     ON client_context(client_id);
CREATE INDEX IF NOT EXISTS idx_client_context_onboarded  ON client_context(onboarding_complete) WHERE onboarding_complete = true;

DROP TRIGGER IF EXISTS trg_client_context_updated_at ON client_context;
CREATE TRIGGER trg_client_context_updated_at BEFORE UPDATE ON client_context
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE client_context ENABLE ROW LEVEL SECURITY;

CREATE POLICY "client_context inherits clients RLS"
  ON client_context FOR ALL
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

CREATE POLICY "Service role manages client_context"
  ON client_context FOR ALL
  USING (auth.role() = 'service_role');

-- ─── §2 · social_accounts · 11 cols OAuth Fase 2 ready ───────────────
-- Nota: 'access_token' (00001) y 'access_token_encrypted' (V3) coexisten
-- durante migración · vault Fase 2 (DEBT-040) llenará el _encrypted y
-- vaciará el legacy. Idem 'account_id' ↔ 'platform_account_id'.
ALTER TABLE social_accounts
  ADD COLUMN IF NOT EXISTS oauth_status            text NOT NULL DEFAULT 'not_connected'
    CHECK (oauth_status IN ('not_connected','connecting','connected','expired','revoked')),
  ADD COLUMN IF NOT EXISTS platform_account_id     text,
  ADD COLUMN IF NOT EXISTS access_token_encrypted  text,
  ADD COLUMN IF NOT EXISTS token_expires_at        timestamptz,
  ADD COLUMN IF NOT EXISTS is_business_account     boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS linked_facebook_page_id text,
  ADD COLUMN IF NOT EXISTS connection_metadata     jsonb NOT NULL DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS approx_followers        integer CHECK (approx_followers IS NULL OR approx_followers >= 0),
  ADD COLUMN IF NOT EXISTS publishing_frequency    text,
  ADD COLUMN IF NOT EXISTS auto_publish_allowed    boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS is_primary              boolean NOT NULL DEFAULT false;

-- Solo una cuenta primary por cliente
CREATE UNIQUE INDEX IF NOT EXISTS uniq_social_primary_per_client
  ON social_accounts(client_id) WHERE is_primary = true;

-- ─── §3 · brand_files · 3 cols (mime/url/category) ───────────────────
-- Aliases legacy preservados: filename↔file_name · size_bytes↔file_size
-- · storage_path↔file_path · application capa normaliza al leer.
ALTER TABLE brand_files
  ADD COLUMN IF NOT EXISTS mime_type     text,
  ADD COLUMN IF NOT EXISTS storage_url   text,
  ADD COLUMN IF NOT EXISTS file_category text
    CHECK (file_category IN ('logo','brand_guide','sample_content','other'));

-- ─── §4 · client_brand_assets (colores + fonts + FK brand_files) ─────
CREATE TABLE IF NOT EXISTS client_brand_assets (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id            uuid NOT NULL UNIQUE REFERENCES clients(id) ON DELETE CASCADE,
  primary_color        text CHECK (primary_color   IS NULL OR primary_color   ~* '^#[0-9A-Fa-f]{6}$'),
  secondary_color      text CHECK (secondary_color IS NULL OR secondary_color ~* '^#[0-9A-Fa-f]{6}$'),
  accent_color         text CHECK (accent_color    IS NULL OR accent_color    ~* '^#[0-9A-Fa-f]{6}$'),
  font_primary         text,
  font_secondary       text,
  logo_file_id         uuid REFERENCES brand_files(id) ON DELETE SET NULL,
  brand_guide_file_id  uuid REFERENCES brand_files(id) ON DELETE SET NULL,
  created_at           timestamptz NOT NULL DEFAULT now(),
  updated_at           timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_client_brand_assets_client ON client_brand_assets(client_id);

DROP TRIGGER IF EXISTS trg_client_brand_assets_updated_at ON client_brand_assets;
CREATE TRIGGER trg_client_brand_assets_updated_at BEFORE UPDATE ON client_brand_assets
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE client_brand_assets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "client_brand_assets inherits clients RLS"
  ON client_brand_assets FOR ALL
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

CREATE POLICY "Service role manages client_brand_assets"
  ON client_brand_assets FOR ALL
  USING (auth.role() = 'service_role');

-- ─── §5 · brand_voice_corpus · índice compuesto recency ─────────────
-- ARIA context builder lee últimos N samples ordenados por created_at.
CREATE INDEX IF NOT EXISTS idx_brand_voice_corpus_client_created
  ON brand_voice_corpus (client_id, created_at DESC);

-- ═════════════════════════════════════════════════════════════════════
-- Verificación post-apply (SELECT manual en SQL Editor):
--   SELECT table_name FROM information_schema.tables
--     WHERE table_schema='public'
--     AND table_name IN ('client_context','client_brand_assets');
--   -- Esperado: 2 filas
--   SELECT count(*) FROM information_schema.columns
--     WHERE table_name='social_accounts' AND table_schema='public';
--   -- Esperado: 20 (9 originales + 11 nuevas)
-- ═════════════════════════════════════════════════════════════════════
