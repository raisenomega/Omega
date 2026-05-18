-- ═══════════════════════════════════════════════════════════════════
-- OmegaRaisen — Migración 00001: Initial Consolidated Schema
-- Consolida las 25 migraciones de los 3 directorios viejos en una sola.
-- Apply order: 00001 → 00002 → 00003
-- ═══════════════════════════════════════════════════════════════════

-- ─── EXTENSIONES ──────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";       -- pgvector V3
CREATE EXTENSION IF NOT EXISTS "pg_cron";      -- futuro auto-evaluación

-- ─── PROFILES (extends auth.users) ────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
  id          uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email       text UNIQUE NOT NULL,
  full_name   text,
  avatar_url  text,
  role        text NOT NULL DEFAULT 'client' CHECK (role IN ('owner','admin','reseller','client','viewer')),
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Service role manages profiles"
  ON profiles FOR ALL
  USING (auth.role() = 'service_role');

-- ─── RESELLERS (white-label tenancy) ──────────────────────────────
CREATE TABLE IF NOT EXISTS resellers (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_user_id uuid NOT NULL REFERENCES auth.users(id),
  name          text NOT NULL,
  slug          text UNIQUE NOT NULL,
  custom_domain text UNIQUE,
  status        text NOT NULL DEFAULT 'active' CHECK (status IN ('active','paused','suspended')),
  plan          text NOT NULL DEFAULT 'basic' CHECK (plan IN ('basic','pro','enterprise')),
  stripe_account_id  text,
  stripe_customer_id text,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE resellers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Resellers view own data"
  ON resellers FOR SELECT
  USING (auth.uid() = owner_user_id);

CREATE POLICY "Resellers update own data"
  ON resellers FOR UPDATE
  USING (auth.uid() = owner_user_id);

CREATE POLICY "Service role manages resellers"
  ON resellers FOR ALL
  USING (auth.role() = 'service_role');

-- ─── RESELLER BRANDING ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reseller_branding (
  reseller_id  uuid PRIMARY KEY REFERENCES resellers(id) ON DELETE CASCADE,
  logo_url     text,
  primary_color   text DEFAULT '#6366f1',
  secondary_color text DEFAULT '#8b5cf6',
  tagline      text,
  custom_css   text,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE reseller_branding ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Resellers view own branding"
  ON reseller_branding FOR SELECT
  USING (reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid()));

CREATE POLICY "Resellers update own branding"
  ON reseller_branding FOR UPDATE
  USING (reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid()));

CREATE POLICY "Service role manages branding"
  ON reseller_branding FOR ALL
  USING (auth.role() = 'service_role');

-- ─── CLIENTS ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clients (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  reseller_id   uuid NOT NULL REFERENCES resellers(id) ON DELETE CASCADE,
  user_id       uuid REFERENCES auth.users(id),
  name          text NOT NULL,
  business_type text,
  industry      text,
  description   text,
  brand_voice   jsonb DEFAULT '{}'::jsonb,
  target_audience jsonb DEFAULT '{}'::jsonb,
  status        text NOT NULL DEFAULT 'active' CHECK (status IN ('active','paused','archived')),
  plan          text NOT NULL DEFAULT 'basic',
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_clients_reseller ON clients(reseller_id);
CREATE INDEX idx_clients_user     ON clients(user_id);
CREATE INDEX idx_clients_status   ON clients(status);

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Clients viewable by their reseller and themselves"
  ON clients FOR SELECT
  USING (
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  );

CREATE POLICY "Resellers manage their clients"
  ON clients FOR ALL
  USING (reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid()));

CREATE POLICY "Service role manages clients"
  ON clients FOR ALL
  USING (auth.role() = 'service_role');

-- ─── SUB-BRANDS (client can have multiple brands) ─────────────────
CREATE TABLE IF NOT EXISTS sub_brands (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  name          text NOT NULL,
  description   text,
  brand_voice   jsonb DEFAULT '{}'::jsonb,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_subbrands_client ON sub_brands(client_id);

ALTER TABLE sub_brands ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Sub-brands inherit client RLS"
  ON sub_brands FOR ALL
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

-- ─── BRAND FILES (client assets) ──────────────────────────────────
CREATE TABLE IF NOT EXISTS brand_files (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  filename      text NOT NULL,
  storage_path  text NOT NULL,
  file_type     text NOT NULL,
  size_bytes    bigint,
  uploaded_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_brandfiles_client ON brand_files(client_id);
ALTER TABLE brand_files ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Brand files inherit client RLS"
  ON brand_files FOR ALL
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

-- ─── SOCIAL ACCOUNTS (OAuth tokens encrypted) ─────────────────────
CREATE TABLE IF NOT EXISTS social_accounts (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  platform      text NOT NULL CHECK (platform IN ('instagram','facebook','twitter','linkedin','tiktok','youtube')),
  account_name  text NOT NULL,
  account_id    text,
  access_token  text,                          -- encrypted at rest via Supabase
  refresh_token text,                          -- encrypted at rest
  expires_at    timestamptz,
  status        text NOT NULL DEFAULT 'active' CHECK (status IN ('active','expired','disconnected')),
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE(client_id, platform, account_id)
);

CREATE INDEX idx_socialaccounts_client ON social_accounts(client_id);
ALTER TABLE social_accounts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Social accounts inherit client RLS"
  ON social_accounts FOR ALL
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

-- ─── CONTENT LAB — generated content drafts ───────────────────────
CREATE TABLE IF NOT EXISTS content_lab_generated (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  sub_brand_id    uuid REFERENCES sub_brands(id) ON DELETE SET NULL,
  agent_code      text NOT NULL,
  content_type    text NOT NULL CHECK (content_type IN ('text','image','video','carousel')),
  prompt          text,
  generated_text  text,
  media_urls      jsonb DEFAULT '[]'::jsonb,
  metadata        jsonb DEFAULT '{}'::jsonb,
  confidence      integer CHECK (confidence BETWEEN 0 AND 10),
  status          text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','approved','rejected','scheduled','published')),
  brand_voice_score numeric(3,2),
  compliance_passed boolean DEFAULT false,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_contentlab_client ON content_lab_generated(client_id);
CREATE INDEX idx_contentlab_status ON content_lab_generated(status);

ALTER TABLE content_lab_generated ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Content lab inherits client RLS"
  ON content_lab_generated FOR ALL
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

-- ─── SCHEDULED POSTS ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS scheduled_posts (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  social_account_id uuid REFERENCES social_accounts(id) ON DELETE SET NULL,
  content_id      uuid REFERENCES content_lab_generated(id) ON DELETE SET NULL,
  scheduled_for   timestamptz NOT NULL,
  status          text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','publishing','published','failed','cancelled')),
  platform_post_id text,
  error_message   text,
  attempts        integer NOT NULL DEFAULT 0,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_scheduledposts_client ON scheduled_posts(client_id);
CREATE INDEX idx_scheduledposts_status_time ON scheduled_posts(status, scheduled_for);

ALTER TABLE scheduled_posts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Scheduled posts inherit client RLS"
  ON scheduled_posts FOR ALL
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

-- ─── AGENTS (37 AI + 45 organizational) ───────────────────────────
CREATE TABLE IF NOT EXISTS agents (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code          text UNIQUE NOT NULL,
  name          text NOT NULL,
  category      text NOT NULL,
  description   text,
  model_tier    text NOT NULL CHECK (model_tier IN ('haiku','sonnet','opus')),
  system_prompt text,
  is_active     boolean NOT NULL DEFAULT true,
  is_premium    boolean NOT NULL DEFAULT false,
  config        jsonb DEFAULT '{}'::jsonb,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_agents_code ON agents(code);
CREATE INDEX idx_agents_active ON agents(is_active);

ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone authenticated can read agents catalog"
  ON agents FOR SELECT
  USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');
CREATE POLICY "Only service role modifies agents"
  ON agents FOR INSERT WITH CHECK (auth.role() = 'service_role');
CREATE POLICY "Only service role updates agents"
  ON agents FOR UPDATE USING (auth.role() = 'service_role');

-- ─── RESELLER AGENTS (which agents a reseller has activated) ──────
CREATE TABLE IF NOT EXISTS reseller_agents (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  reseller_id   uuid NOT NULL REFERENCES resellers(id) ON DELETE CASCADE,
  agent_id      uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  is_enabled    boolean NOT NULL DEFAULT true,
  custom_config jsonb DEFAULT '{}'::jsonb,
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE(reseller_id, agent_id)
);

ALTER TABLE reseller_agents ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Reseller agents inherit reseller RLS"
  ON reseller_agents FOR ALL
  USING (reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid()));

-- ─── ANALYTICS ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS analytics_events (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  scheduled_post_id uuid REFERENCES scheduled_posts(id) ON DELETE SET NULL,
  platform        text NOT NULL,
  event_type      text NOT NULL,
  metric_value    numeric,
  event_data      jsonb DEFAULT '{}'::jsonb,
  occurred_at     timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_analytics_client_time ON analytics_events(client_id, occurred_at DESC);
CREATE INDEX idx_analytics_post ON analytics_events(scheduled_post_id);

ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Analytics inherit client RLS"
  ON analytics_events FOR SELECT
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));
CREATE POLICY "Service role writes analytics"
  ON analytics_events FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- ─── LEADS (gestión de prospects para resellers) ──────────────────
CREATE TABLE IF NOT EXISTS leads (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  reseller_id     uuid NOT NULL REFERENCES resellers(id) ON DELETE CASCADE,
  email           text NOT NULL,
  name            text,
  phone           text,
  source          text,
  status          text NOT NULL DEFAULT 'new' CHECK (status IN ('new','contacted','qualified','converted','lost')),
  consent_given   boolean NOT NULL DEFAULT false,
  consent_date    timestamptz,
  notes           text,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_leads_reseller ON leads(reseller_id);
CREATE INDEX idx_leads_status ON leads(status);

ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Leads inherit reseller RLS"
  ON leads FOR ALL
  USING (reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid()));

-- ─── STRIPE WEBHOOK EVENTS (idempotencia) ─────────────────────────
CREATE TABLE IF NOT EXISTS stripe_webhook_events (
  id              text PRIMARY KEY,                          -- event ID de Stripe (es)
  type            text NOT NULL,
  data            jsonb NOT NULL,
  processed_at    timestamptz NOT NULL DEFAULT now(),
  success         boolean,
  error_message   text
);

CREATE INDEX idx_stripe_events_type_time ON stripe_webhook_events(type, processed_at DESC);

ALTER TABLE stripe_webhook_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role only"
  ON stripe_webhook_events FOR ALL
  USING (auth.role() = 'service_role');

-- ─── FEATURE USAGE TRACKING ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS feature_usage (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  feature_code    text NOT NULL,
  usage_count     integer NOT NULL DEFAULT 1,
  cost_usd        numeric(10,4) DEFAULT 0,
  period_start    timestamptz NOT NULL,
  period_end      timestamptz,
  metadata        jsonb DEFAULT '{}'::jsonb
);

CREATE INDEX idx_featureusage_client ON feature_usage(client_id);
CREATE INDEX idx_featureusage_period ON feature_usage(period_start, period_end);

ALTER TABLE feature_usage ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Feature usage inherits client RLS"
  ON feature_usage FOR SELECT
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));
CREATE POLICY "Service role writes feature usage"
  ON feature_usage FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- ─── UPSELL REQUESTS ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS upsell_requests (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  agent_id        uuid REFERENCES agents(id),
  requested_by    uuid REFERENCES auth.users(id),
  status          text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','approved','rejected','paid')),
  amount_usd      numeric(10,2),
  approved_by     uuid REFERENCES auth.users(id),
  approved_at     timestamptz,
  stripe_payment_intent_id text,
  created_at      timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE upsell_requests ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Upsell requests inherit client RLS"
  ON upsell_requests FOR ALL
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));

-- ═══════════════════════════════════════════════════════════════════
-- TRIGGER: updated_at automático
-- ═══════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
  t text;
BEGIN
  FOR t IN
    SELECT table_name FROM information_schema.columns
    WHERE column_name = 'updated_at' AND table_schema = 'public'
  LOOP
    EXECUTE format('
      DROP TRIGGER IF EXISTS set_updated_at ON %I;
      CREATE TRIGGER set_updated_at
        BEFORE UPDATE ON %I
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    ', t, t);
  END LOOP;
END$$;

-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00001
-- Próxima: 00002_agent_memory_pgvector.sql
-- ═══════════════════════════════════════════════════════════════════
