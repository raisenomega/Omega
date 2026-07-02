-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00085 · landing_cms                                    ║
-- ║  02 jul 2026 · Arco Landing OMEGA · Fase 2 · contenido editable     ║
-- ║                                                                   ║
-- ║  Tablas donde vive el contenido de la landing pública (réplica del ║
-- ║  modelo raisen-ag · prefijo landing_ para higiene de namespace).   ║
-- ║  9 tablas: landing_sections · landing_services · landing_metrics ·  ║
-- ║  landing_testimonials · landing_process_steps · landing_pricing_    ║
-- ║  tiers · landing_pricing_addons · landing_footer_config ·           ║
-- ║  landing_footer_social_links. Esquemas bilingües _es/_en del molde. ║
-- ║                                                                   ║
-- ║  RLS patrón OMEGA-plataforma (NO el is_admin() del molde):          ║
-- ║   · lectura PÚBLICA (FOR SELECT USING true · la landing es pública) ║
-- ║   · escritura SOLO super_owner (FOR ALL · EXISTS is_super_owner ·   ║
-- ║     mismo patrón singleton de la policy de leads en 00084).         ║
-- ║                                                                   ║
-- ║  SEED idempotente: site_sections ON CONFLICT(name) · el resto       ║
-- ║  seed-if-empty (WHERE NOT EXISTS · las tablas del molde no traen     ║
-- ║  clave natural única). metrics y testimonials SIN seed (P1 · vacías ║
-- ║  · el owner las llena desde el editor en F5). Precios canónicos     ║
-- ║  DECISIÓN-PRECIOS-2026: $0/$29/$97/$269 · Video Packs $39/$95/$125.  ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─────────────────────────────────────────────────────────────────────
-- 1) TABLAS (esquemas del molde · prefijo landing_)
-- ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS landing_sections (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name          text NOT NULL UNIQUE,
  is_visible    boolean NOT NULL DEFAULT true,
  display_order int NOT NULL DEFAULT 0,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS landing_services (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  icon           text NOT NULL DEFAULT 'Target',
  title_es       text NOT NULL,
  title_en       text NOT NULL,
  description_es text NOT NULL,
  description_en text NOT NULL,
  benefits_es    text[] NOT NULL DEFAULT '{}',
  benefits_en    text[] NOT NULL DEFAULT '{}',
  display_order  int NOT NULL DEFAULT 0,
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS landing_metrics (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  metric_key    text NOT NULL UNIQUE,
  value         numeric NOT NULL,
  suffix        text NOT NULL DEFAULT '',
  label_es      text NOT NULL,
  label_en      text NOT NULL,
  display_order int NOT NULL DEFAULT 0,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS landing_testimonials (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name          text NOT NULL,
  role_es       text NOT NULL,
  role_en       text NOT NULL,
  company       text NOT NULL,
  quote_es      text NOT NULL,
  quote_en      text NOT NULL,
  display_order int NOT NULL DEFAULT 0,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS landing_process_steps (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  step_number    int NOT NULL,
  icon           text NOT NULL DEFAULT 'ClipboardCheck',
  title_es       text NOT NULL,
  title_en       text NOT NULL,
  description_es text NOT NULL,
  description_en text NOT NULL,
  display_order  int NOT NULL DEFAULT 0,
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS landing_pricing_tiers (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name_es         text NOT NULL DEFAULT '',
  name_en         text NOT NULL DEFAULT '',
  tagline_es      text NOT NULL DEFAULT '',
  tagline_en      text NOT NULL DEFAULT '',
  price           numeric NOT NULL DEFAULT 0,
  features_es     text[] NOT NULL DEFAULT '{}',
  features_en     text[] NOT NULL DEFAULT '{}',
  is_recommended  boolean NOT NULL DEFAULT false,
  is_visible      boolean NOT NULL DEFAULT true,
  stripe_price_id text NOT NULL DEFAULT '',
  display_order   int NOT NULL DEFAULT 0,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS landing_pricing_addons (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name_es         text NOT NULL DEFAULT '',
  name_en         text NOT NULL DEFAULT '',
  description_es  text NOT NULL DEFAULT '',
  description_en  text NOT NULL DEFAULT '',
  price           numeric NOT NULL DEFAULT 0,
  is_visible      boolean NOT NULL DEFAULT true,
  stripe_price_id text NOT NULL DEFAULT '',
  display_order   int NOT NULL DEFAULT 0,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS landing_footer_config (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  phone      text NOT NULL DEFAULT '',
  email      text NOT NULL DEFAULT '',
  rights_es  text NOT NULL DEFAULT 'Todos los derechos reservados.',
  rights_en  text NOT NULL DEFAULT 'All rights reserved.',
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS landing_footer_social_links (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  platform      text NOT NULL,
  url           text NOT NULL DEFAULT '#',
  icon_name     text NOT NULL,
  display_order int NOT NULL DEFAULT 0,
  is_visible    boolean NOT NULL DEFAULT true,
  created_at    timestamptz NOT NULL DEFAULT now()
);

-- ─────────────────────────────────────────────────────────────────────
-- 2) RLS · lectura pública + escritura solo super_owner (patrón 00084)
--    (permissive · en SELECT la policy pública OR con la de escritura → todos leen;
--     INSERT/UPDATE/DELETE solo los cubre la policy FOR ALL de super_owner)
-- ─────────────────────────────────────────────────────────────────────
ALTER TABLE landing_sections            ENABLE ROW LEVEL SECURITY;
ALTER TABLE landing_services            ENABLE ROW LEVEL SECURITY;
ALTER TABLE landing_metrics             ENABLE ROW LEVEL SECURITY;
ALTER TABLE landing_testimonials        ENABLE ROW LEVEL SECURITY;
ALTER TABLE landing_process_steps       ENABLE ROW LEVEL SECURITY;
ALTER TABLE landing_pricing_tiers       ENABLE ROW LEVEL SECURITY;
ALTER TABLE landing_pricing_addons      ENABLE ROW LEVEL SECURITY;
ALTER TABLE landing_footer_config       ENABLE ROW LEVEL SECURITY;
ALTER TABLE landing_footer_social_links ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "landing_sections public read" ON landing_sections;
CREATE POLICY "landing_sections public read" ON landing_sections FOR SELECT USING (true);
DROP POLICY IF EXISTS "landing_sections super_owner write" ON landing_sections;
CREATE POLICY "landing_sections super_owner write" ON landing_sections FOR ALL
  USING (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true))
  WITH CHECK (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true));

DROP POLICY IF EXISTS "landing_services public read" ON landing_services;
CREATE POLICY "landing_services public read" ON landing_services FOR SELECT USING (true);
DROP POLICY IF EXISTS "landing_services super_owner write" ON landing_services;
CREATE POLICY "landing_services super_owner write" ON landing_services FOR ALL
  USING (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true))
  WITH CHECK (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true));

DROP POLICY IF EXISTS "landing_metrics public read" ON landing_metrics;
CREATE POLICY "landing_metrics public read" ON landing_metrics FOR SELECT USING (true);
DROP POLICY IF EXISTS "landing_metrics super_owner write" ON landing_metrics;
CREATE POLICY "landing_metrics super_owner write" ON landing_metrics FOR ALL
  USING (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true))
  WITH CHECK (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true));

DROP POLICY IF EXISTS "landing_testimonials public read" ON landing_testimonials;
CREATE POLICY "landing_testimonials public read" ON landing_testimonials FOR SELECT USING (true);
DROP POLICY IF EXISTS "landing_testimonials super_owner write" ON landing_testimonials;
CREATE POLICY "landing_testimonials super_owner write" ON landing_testimonials FOR ALL
  USING (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true))
  WITH CHECK (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true));

DROP POLICY IF EXISTS "landing_process_steps public read" ON landing_process_steps;
CREATE POLICY "landing_process_steps public read" ON landing_process_steps FOR SELECT USING (true);
DROP POLICY IF EXISTS "landing_process_steps super_owner write" ON landing_process_steps;
CREATE POLICY "landing_process_steps super_owner write" ON landing_process_steps FOR ALL
  USING (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true))
  WITH CHECK (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true));

DROP POLICY IF EXISTS "landing_pricing_tiers public read" ON landing_pricing_tiers;
CREATE POLICY "landing_pricing_tiers public read" ON landing_pricing_tiers FOR SELECT USING (true);
DROP POLICY IF EXISTS "landing_pricing_tiers super_owner write" ON landing_pricing_tiers;
CREATE POLICY "landing_pricing_tiers super_owner write" ON landing_pricing_tiers FOR ALL
  USING (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true))
  WITH CHECK (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true));

DROP POLICY IF EXISTS "landing_pricing_addons public read" ON landing_pricing_addons;
CREATE POLICY "landing_pricing_addons public read" ON landing_pricing_addons FOR SELECT USING (true);
DROP POLICY IF EXISTS "landing_pricing_addons super_owner write" ON landing_pricing_addons;
CREATE POLICY "landing_pricing_addons super_owner write" ON landing_pricing_addons FOR ALL
  USING (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true))
  WITH CHECK (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true));

DROP POLICY IF EXISTS "landing_footer_config public read" ON landing_footer_config;
CREATE POLICY "landing_footer_config public read" ON landing_footer_config FOR SELECT USING (true);
DROP POLICY IF EXISTS "landing_footer_config super_owner write" ON landing_footer_config;
CREATE POLICY "landing_footer_config super_owner write" ON landing_footer_config FOR ALL
  USING (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true))
  WITH CHECK (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true));

DROP POLICY IF EXISTS "landing_footer_social_links public read" ON landing_footer_social_links;
CREATE POLICY "landing_footer_social_links public read" ON landing_footer_social_links FOR SELECT USING (true);
DROP POLICY IF EXISTS "landing_footer_social_links super_owner write" ON landing_footer_social_links;
CREATE POLICY "landing_footer_social_links super_owner write" ON landing_footer_social_links FOR ALL
  USING (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true))
  WITH CHECK (EXISTS (SELECT 1 FROM resellers WHERE owner_user_id = auth.uid() AND is_super_owner = true));

-- ─────────────────────────────────────────────────────────────────────
-- 3) SEED (idempotente)
-- ─────────────────────────────────────────────────────────────────────
-- Secciones: hero/services/process/lead_form visibles · social_proof y pain_solution
-- ocultas hasta tener contenido real (P1).
INSERT INTO landing_sections (name, is_visible, display_order) VALUES
  ('hero',          true,  1),
  ('pain_solution', false, 2),
  ('services',      true,  3),
  ('social_proof',  false, 4),
  ('process',       true,  5),
  ('lead_form',     true,  6)
ON CONFLICT (name) DO NOTHING;

-- Servicios: 4 tarjetas factuales de la PLATAFORMA (sin métricas inventadas · agentes = 8, canon).
INSERT INTO landing_services (icon, title_es, title_en, description_es, description_en, benefits_es, benefits_en, display_order)
SELECT * FROM (VALUES
  ('Sparkles',    'Content Lab', 'Content Lab',
   'Genera contenido con IA — caption, imagen, video y hashtags — entrenado en tu marca.',
   'Generate content with AI — caption, image, video and hashtags — trained on your brand.',
   ARRAY['Caption, imagen y video','Entrenado en tu voz de marca','Hashtags optimizados']::text[],
   ARRAY['Caption, image and video','Trained on your brand voice','Optimized hashtags']::text[], 1),
  ('CalendarDays','Calendario inteligente', 'Smart calendar',
   'Programa y publica automáticamente en todas tus redes.',
   'Schedule and publish automatically across all your networks.',
   ARRAY['Programación automática','Todas tus redes en un lugar','Publicación sin intervención']::text[],
   ARRAY['Automatic scheduling','All your networks in one place','Hands-off publishing']::text[], 2),
  ('BarChart3',   'Analytics y reportes', 'Analytics and reports',
   'Las métricas reales de tus redes, en un solo lugar.',
   'The real metrics of your networks, in one place.',
   ARRAY['Métricas reales por red','Reportes descargables','Historial de rendimiento']::text[],
   ARRAY['Real metrics per network','Downloadable reports','Performance history']::text[], 3),
  ('Bot',         'Agentes IA a tu servicio', 'AI agents at your service',
   'ARIA te sugiere qué publicar y 8 agentes especializados trabajan por ti.',
   'ARIA suggests what to post and 8 specialized agents work for you.',
   ARRAY['Sugerencias de ARIA','8 agentes especializados','Aprende de tu negocio']::text[],
   ARRAY['ARIA suggestions','8 specialized agents','Learns from your business']::text[], 4)
) AS v(icon, title_es, title_en, description_es, description_en, benefits_es, benefits_en, display_order)
WHERE NOT EXISTS (SELECT 1 FROM landing_services);

-- Pasos del proceso: flujo real de OMEGA (verificado vs onboarding: registro → conectar redes
-- (SectionSocialAccounts/Zernio) → generar+programar (Content Lab) → aprobar+publicar (REX/Zernio)).
INSERT INTO landing_process_steps (step_number, icon, title_es, title_en, description_es, description_en, display_order)
SELECT * FROM (VALUES
  (1, 'UserPlus',    'Regístrate', 'Sign up',
   'Crea tu cuenta gratis en segundos.', 'Create your free account in seconds.', 1),
  (2, 'Link',        'Conecta tus redes', 'Connect your networks',
   'Instagram, Facebook, TikTok y LinkedIn.', 'Instagram, Facebook, TikTok and LinkedIn.', 2),
  (3, 'Sparkles',    'La IA genera y programa', 'AI creates and schedules',
   'Contenido listo con tu voz de marca.', 'Content ready with your brand voice.', 3),
  (4, 'CheckCircle', 'Aprueba y publica', 'Approve and publish',
   'Tú decides, OMEGA publica por ti.', 'You decide, OMEGA publishes for you.', 4)
) AS v(step_number, icon, title_es, title_en, description_es, description_en, display_order)
WHERE NOT EXISTS (SELECT 1 FROM landing_process_steps);

-- Precios canónicos (DECISIÓN-PRECIOS-2026 · $0/$29/$97/$269). Features de MODELO_NEGOCIO §3
-- (los precios internos del doc quedaron desactualizados · los features siguen válidos). Pro recomendado.
INSERT INTO landing_pricing_tiers (name_es, name_en, tagline_es, tagline_en, price, features_es, features_en, is_recommended, display_order)
SELECT * FROM (VALUES
  ('Adopción', 'Adoption', '7 días gratis', '7-day free trial', 0::numeric,
   ARRAY['Todas las funciones desbloqueadas por 7 días','1 cuenta por red (IG · FB · TikTok · LinkedIn)','1 publicación al día','Content Lab, Calendario, Analytics y Media','Asistente ARIA (Nivel 1)']::text[],
   ARRAY['All features unlocked for 7 days','1 account per network (IG · FB · TikTok · LinkedIn)','1 post per day','Content Lab, Calendar, Analytics and Media','ARIA assistant (Level 1)']::text[],
   false, 1),
  ('Básico', 'Basic', 'Para empezar en serio', 'To get started', 29::numeric,
   ARRAY['1 cuenta por red (IG · FB · TikTok · LinkedIn)','8 publicaciones por semana','Content Lab y Brand Voice','1 video de regalo','Asistente ARIA (Nivel 2)']::text[],
   ARRAY['1 account per network (IG · FB · TikTok · LinkedIn)','8 posts per week','Content Lab and Brand Voice','1 free video','ARIA assistant (Level 2)']::text[],
   false, 2),
  ('Pro', 'Pro', 'El favorito de las PYMEs', 'The SMB favorite', 97::numeric,
   ARRAY['2 cuentas por red','16 publicaciones por semana','Todo desbloqueado: Analytics, Calendario, Crisis Room e Imagen','Centro de Inteligencia (análisis web SEO/GEO/AEO)','2 videos incluidos al mes','Asistente ARIA (Nivel 3) + reportes semanales']::text[],
   ARRAY['2 accounts per network','16 posts per week','Everything unlocked: Analytics, Calendar, Crisis Room and Image','Intelligence Center (web analysis SEO/GEO/AEO)','2 videos included per month','ARIA assistant (Level 3) + weekly reports']::text[],
   true, 3),
  ('Enterprise', 'Enterprise', 'Máximo poder', 'Maximum power', 269::numeric,
   ARRAY['3 cuentas por red (12 en total)','Todo de Pro ×3, sin funciones bloqueadas','300 imágenes extra al mes','150 análisis del Centro de Inteligencia al mes','Asistente ARIA (Nivel 4) + análisis semanal','Soporte prioritario']::text[],
   ARRAY['3 accounts per network (12 total)','Everything in Pro ×3, no locked features','300 extra images per month','150 Intelligence Center analyses per month','ARIA assistant (Level 4) + weekly analysis','Priority support']::text[],
   false, 4)
) AS v(name_es, name_en, tagline_es, tagline_en, price, features_es, features_en, is_recommended, display_order)
WHERE NOT EXISTS (SELECT 1 FROM landing_pricing_tiers);

-- Video Packs (add-ons · $39/$95/$125). Descripción de posicionamiento sin inventar conteos
-- exactos (el detalle por pack lo confirma el owner en el editor · F5).
INSERT INTO landing_pricing_addons (name_es, name_en, description_es, description_en, price, display_order)
SELECT * FROM (VALUES
  ('Video Pack Starter',   'Video Pack Starter',   'Videos con IA para empezar.',            'AI videos to get started.',        39::numeric, 1),
  ('Video Pack Creator',   'Video Pack Creator',   'Más videos con IA para crecer.',         'More AI videos to grow.',          95::numeric, 2),
  ('Video Pack Cinematic', 'Video Pack Cinematic', 'Videos con IA de máxima producción.',    'AI videos, top production.',       125::numeric, 3)
) AS v(name_es, name_en, description_es, description_en, price, display_order)
WHERE NOT EXISTS (SELECT 1 FROM landing_pricing_addons);

-- Footer: marca OMEGA · "Una plataforma de Raisen Agency" (Raisen solo en footer · decisión cerrada).
-- phone/email vacíos (el owner los completa en F5 · P1: no inventar contacto).
INSERT INTO landing_footer_config (phone, email, rights_es, rights_en)
SELECT '', '',
  'Una plataforma de Raisen Agency. Todos los derechos reservados.',
  'A Raisen Agency platform. All rights reserved.'
WHERE NOT EXISTS (SELECT 1 FROM landing_footer_config);

-- landing_footer_social_links: SIN seed (P1 · el owner agrega las URLs reales en F5 · no inventar).
-- landing_metrics / landing_testimonials: SIN seed (P1 · vacías · el owner las llena en F5).
