-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00081 · strategies.last_used                           ║
-- ║  ARCO MEDICIÓN · CAPA 1 · "ver qué usé en la tarjeta usada"        ║
-- ║                                                                   ║
-- ║  Registra el ÚLTIMO uso de una estrategia: qué red (o "completa"), ║
-- ║  qué texto/brief se mandó a Content Lab, y cuándo. Se escribe al   ║
-- ║  click de "Usar" (completa) o de la flecha por red. NULL = nunca   ║
-- ║  usada (honesto · las filas viejas quedan NULL).                  ║
-- ║                                                                   ║
-- ║  ADITIVA · NULLABLE · hereda el RLS de strategies (00043:31-49).   ║
-- ║  NO toca content_lab_generated ni scheduled_posts → cero impacto   ║
-- ║  en generar/publicar. Riesgo cero. CAPA 2 (vínculo al post +       ║
-- ║  rendimiento) = otra migración/columna, ortogonal a ésta.         ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- IF NOT EXISTS: idempotente · si ya se aplicó por Postgres directo (CEO-gate), `supabase db push`
-- la corre como no-op y la registra en el historial sin fallar (42701).
ALTER TABLE strategies ADD COLUMN IF NOT EXISTS last_used jsonb;

COMMENT ON COLUMN strategies.last_used IS
  'Último uso registrado: {platform, brief, at}. NULL = nunca usada. CAPA 1 medición.';
