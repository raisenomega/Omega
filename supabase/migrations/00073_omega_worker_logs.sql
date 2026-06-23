-- 00073 · omega_worker_logs · log de corridas de workers (R-OPS-001 · DEBT-WORKER-LOGS).
--
-- POR QUÉ: base_worker.py (BaseWorker._log) escribe acá el estado de cada corrida (started/completed/
-- failed/disabled) · la tabla FALTABA → PGRST205 → rex_publisher (y todo worker) falla el DB-log
-- silencioso (cae a stdout). NO confundir con omega_error_registry (SENTINEL · existe · otra cosa).
--
-- CRUCE código↔tabla (base_worker._log INSERT/UPDATE/SELECT): id="{worker}_{client_id}_{ms}" (TEXT
-- compuesto · NO uuid · uuid rompería el INSERT) · worker_name · client_id · status · result(jsonb) ·
-- error(nullable) · duration_ms. created_at = audit (el código no lo escribe → default). updated_at
-- OMITIDO (el UPDATE del código no lo toca → sería columna muerta).
--
-- DRY-RUN read-only prod (23 jun · rwlnihoqhxwpbehibgxu): omega_worker_logs NO existe · clients existe.
-- RLS = copia VERBATIM de social_accounts/social_metrics (aislamiento por dueño · probada · el worker
-- escribe con service-role que bypasea RLS · un reseller no ve logs de otro negocio).

CREATE TABLE public.omega_worker_logs (
  id           text PRIMARY KEY,
  worker_name  text NOT NULL,
  client_id    uuid NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
  status       text NOT NULL CHECK (status IN ('started', 'completed', 'failed', 'disabled')),
  result       jsonb NOT NULL DEFAULT '{}'::jsonb,
  error        text,
  duration_ms  integer NOT NULL DEFAULT 0,
  created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_omega_worker_logs_worker_client ON public.omega_worker_logs(worker_name, client_id);

ALTER TABLE public.omega_worker_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "omega_worker_logs inherit client RLS"
  ON public.omega_worker_logs FOR ALL
  USING (client_id IN (SELECT id FROM clients WHERE
    user_id = auth.uid()
    OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
  ));
