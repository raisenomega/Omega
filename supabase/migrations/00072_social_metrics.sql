-- 00072 · social_metrics · histórico de métricas sociales (Arco 1 · pipeline familia 1 = Zernio
-- social organic). El cron `social_metrics_snapshot` (Fase 2) puebla esto a diario.
--
-- POR QUÉ: Zernio daily-metrics NO tiene ventana (ignora date-params · verificado) → sin histórico
-- propio no hay "últimos 90 días" reales ni base contra qué LUAN evalúa `was_correct`. Esta tabla
-- es el almacén. Familia 2 (ads) y 3 (web/SEO) = tablas hermanas FUTURAS (ads_metrics/web_metrics ·
-- tipadas · llaves propias) — NO se tocan acá (forward-compat por aislamiento, no por jsonb).
--
-- LLAVE: client_id (RLS-nativo · negocio OMEGA) + profile_id como traza (de qué profile Zernio salió ·
-- 1:1 con el cliente). UNIQUE(client_id, platform, metric_date) = idempotencia (upsert · re-correr no
-- duplica). GRANO: actividad per-día (Zernio la da en dailyData) · followers = snapshot diario del total.
--
-- HONESTIDAD P1: TODAS las métricas NULLABLE → NULL = "no hay dato ese día" (NUNCA 0 ni interpolación).
-- Un día sin snapshot = fila AUSENTE, no inventada (huecos honestos > relleno · lo que LUAN necesita).
--
-- DRY-RUN read-only prod (22 jun · rwlnihoqhxwpbehibgxu): social_metrics NO existe · clients existe ·
-- CHECK platform == el de social_accounts/00071 EXACTO (7) · RLS = copia VERBATIM de la policy probada
-- de social_accounts (mismo aislamiento client→user/reseller). Aplicar a prod ANTES del cron (Fase 2).

CREATE TABLE public.social_metrics (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id    uuid NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
  profile_id   text NOT NULL,
  platform     text NOT NULL CHECK (platform IN ('instagram', 'facebook', 'tiktok', 'twitter', 'linkedin', 'youtube', 'reddit')),
  metric_date  date NOT NULL,
  followers    integer,   -- snapshot del followersCount (Zernio solo da el total actual · NULL si no se obtuvo)
  reach        integer,
  impressions  integer,
  likes        integer,
  comments     integer,
  shares       integer,
  saves        integer,
  views        integer,
  post_count   integer,
  captured_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (client_id, platform, metric_date)
);

CREATE INDEX idx_social_metrics_client_date ON public.social_metrics(client_id, metric_date);

ALTER TABLE public.social_metrics ENABLE ROW LEVEL SECURITY;

-- Copia VERBATIM de la policy probada de social_accounts (no se inventa · mismo aislamiento por dueño).
-- El cron escribe con service_role (BYPASSRLS) · esta policy protege las lecturas del cliente/reseller.
CREATE POLICY "social_metrics inherit client RLS"
  ON public.social_metrics FOR ALL
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));
