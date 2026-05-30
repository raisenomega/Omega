-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00044 · strategies.generation_key                      ║
-- ║  30 may 2026 · DEBT-096 Fase 2 · idempotencia del cron            ║
-- ║                                                                   ║
-- ║  El cron de estrategias (Fase 2) genera 1 estrategia auto por     ║
-- ║  (cliente, día). generation_key = '{client_id}:{YYYY-MM-DD}'.     ║
-- ║  UNIQUE garantiza idempotencia a nivel DB (sobrevive reinicio de  ║
-- ║  Railway / doble-corrida / bug). Las estrategias manuales (Fase 1)║
-- ║  llevan key=NULL y NO participan del índice (UNIQUE parcial).     ║
-- ║  Sin tocar limits_omega · SHA1 intacto.                           ║
-- ╚═══════════════════════════════════════════════════════════════════╝

ALTER TABLE strategies
  ADD COLUMN IF NOT EXISTS generation_key text;

-- Idempotencia del cron: 1 estrategia auto por (cliente, día). Manual = NULL (no participa).
-- UNIQUE PARCIAL → solo aplica a filas con key; los manuales (NULL) conviven sin conflicto.
CREATE UNIQUE INDEX IF NOT EXISTS uq_strategies_generation_key
  ON strategies (generation_key) WHERE generation_key IS NOT NULL;
