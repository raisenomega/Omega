-- 00066_scheduled_posts_account_guard.sql (8 jun 2026)
-- Cierra `sin_red` de raiz. El fan-out por red (metadata.platforms -> 1 scheduled_post por red marcada,
-- cada uno con su social_account_id resuelto de la cuenta status='active') ya evita generar pending con
-- social_account_id NULL. Este guard es la red de seguridad a nivel DB: impide que una regresion futura
-- vuelva a crear el estado invalido que disparaba el toast "Conecta la red primero".
--
-- TRANSACCIONAL (savepoint implicito): si por una carrera quedara una fila violadora, el ADD CONSTRAINT
-- falla y TODO el archivo revierte. Orden de despliegue: CODIGO PRIMERO (backend fan-out ya live, nunca
-- inserta NULL) -> luego esta migracion. Asi no hay ventana donde el codigo viejo viole el CHECK.

-- (1) Backfill: las pending con social_account_id NULL son estado invalido (no publican · darian sin_red).
--     Se cancelan; los drafts en content_lab_generated sobreviven -> re-aprobables con el picker de redes.
--     Idempotente: tras la primera corrida, 0 filas.
UPDATE scheduled_posts SET status = 'cancelled'
WHERE status = 'pending' AND social_account_id IS NULL;

-- (2) Guard: un post publicable NO puede existir sin red. published_manual (marca DB, no publica via Zernio)
--     y cancelled quedan exentos (carve-out real · esas filas legitimamente no tienen social_account_id).
ALTER TABLE scheduled_posts
  ADD CONSTRAINT scheduled_posts_account_required
  CHECK (social_account_id IS NOT NULL OR status IN ('published_manual', 'cancelled'));
