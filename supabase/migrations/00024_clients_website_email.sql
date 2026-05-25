-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00024 · clients.website + business_email               ║
-- ║  25 may 2026 · sección 1 wizard (Identidad) · campos opcionales    ║
-- ║                                                                    ║
-- ║  Datos del negocio capturados en onboarding · sin default ·        ║
-- ║  aditiva · idempotente · cero cambios destructivos.               ║
-- ╚═══════════════════════════════════════════════════════════════════╝

ALTER TABLE clients
  ADD COLUMN IF NOT EXISTS website        text,
  ADD COLUMN IF NOT EXISTS business_email text;
