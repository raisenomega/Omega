-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00082 · strategy_idea_usages                           ║
-- ║  29 jun 2026 · REDISEÑO Estrategias Fase A · "la idea es la unidad" ║
-- ║                                                                   ║
-- ║  1 fila por IDEA usada de una estrategia (no por estrategia).      ║
-- ║  Soporta "Usadas muestra ideas sueltas" (brief por idea + re-usar) ║
-- ║  y el flip a estado='used' cuando se usan TODAS las ideas.         ║
-- ║  ADITIVA: tabla nueva · no altera strategies (last_used queda como ║
-- ║  denormalización · no estorba). RLS client-scoped desde creación.  ║
-- ║  ON DELETE CASCADE coherente con DELETE /strategies/{id} (sin      ║
-- ║  huérfanos). UNIQUE(strategy_id, idea_idx) = re-usar no duplica.   ║
-- ╚═══════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS strategy_idea_usages (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id  uuid NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
  client_id    uuid NOT NULL REFERENCES clients(id) ON DELETE CASCADE,  -- denormalizado · filtra sin join
  idea_idx     integer NOT NULL,                                        -- índice en posts_sugeridos (write-once)
  platform     text,                                                    -- red normalizada de la idea
  brief        text,                                                    -- texto de la idea usada (Usadas + re-usar)
  used_at      timestamptz NOT NULL DEFAULT now(),
  UNIQUE (strategy_id, idea_idx)                                        -- una idea = usada 1 vez · idempotente
);

-- List de "Usadas" del cliente (todas las ideas usadas de sus estrategias).
CREATE INDEX IF NOT EXISTS idx_strategy_idea_usages_client ON strategy_idea_usages (client_id);

ALTER TABLE strategy_idea_usages ENABLE ROW LEVEL SECURITY;

-- Cliente ve solo los usos de SUS estrategias · reseller los de sus clientes (patrón 00043).
DROP POLICY IF EXISTS "idea_usages client read" ON strategy_idea_usages;
CREATE POLICY "idea_usages client read"
  ON strategy_idea_usages FOR SELECT
  USING (
    client_id IN (
      SELECT id FROM clients
      WHERE user_id = auth.uid()
         OR reseller_id IN (SELECT id FROM resellers WHERE owner_user_id = auth.uid())
    )
  );

-- service_role gestiona (registrar uso de idea, leer para el list, borrar en cascade).
DROP POLICY IF EXISTS "idea_usages service_role all" ON strategy_idea_usages;
CREATE POLICY "idea_usages service_role all"
  ON strategy_idea_usages FOR ALL
  USING (auth.role() = 'service_role');
