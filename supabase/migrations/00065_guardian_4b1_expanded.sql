-- 00065_guardian_4b1_expanded.sql
-- GUARDIAN 4B-1 expandido · ALTER del schema 00022 (NO recrea tablas) + columnas del ask ampliado.
-- session_id (tracking cross-event por sesión) · device_fingerprint (DEBT-GUARDIAN-DEVICE-FINGERPRINTING
-- activa la extracción) · resolution_notes (notas del owner al resolver). Aditiva · idempotente.
-- country/geo ya existen nullable en 00022 (schema-ready §7.6) · este sprint activa el geo lookup (IPinfo).

ALTER TABLE user_security_log ADD COLUMN IF NOT EXISTS session_id text;
ALTER TABLE user_security_log ADD COLUMN IF NOT EXISTS device_fingerprint text;
ALTER TABLE security_incidents ADD COLUMN IF NOT EXISTS resolution_notes text;

CREATE INDEX IF NOT EXISTS idx_usl_risk_high ON user_security_log(risk_score DESC) WHERE risk_score >= 50;
CREATE INDEX IF NOT EXISTS idx_usl_session ON user_security_log(session_id) WHERE session_id IS NOT NULL;

COMMENT ON COLUMN user_security_log.session_id IS 'Supabase auth session id · tracking cross-event por sesión';
COMMENT ON COLUMN user_security_log.device_fingerprint IS 'Browser/OS desde user_agent · DEBT-GUARDIAN-DEVICE-FINGERPRINTING activa extracción';
COMMENT ON COLUMN security_incidents.resolution_notes IS 'Notas del owner al resolver/marcar el incidente';

-- ═══════════════════════════════════════════════════════════════════
-- Verificación: SELECT column_name FROM information_schema.columns
--   WHERE table_name='user_security_log' AND column_name IN ('session_id','device_fingerprint'); -- 2 filas
-- ═══════════════════════════════════════════════════════════════════
