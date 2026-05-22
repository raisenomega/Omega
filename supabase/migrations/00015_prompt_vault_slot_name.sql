-- ═══════════════════════════════════════════════════════════════════
-- Migración 00015 · prompt_vault.slot_name
-- Añade slot_name para distinguir variantes del mismo (category, vertical, platform).
-- Razón: 4 colisiones detectadas al seedear los 30 prompts §5 (e.g. dos captions
-- de restaurant/instagram: 'daily_special' vs 'weekend_event').
-- Reemplaza la UNIQUE de 00014 por una que incluye slot_name.
-- ═══════════════════════════════════════════════════════════════════

ALTER TABLE prompt_vault
  ADD COLUMN IF NOT EXISTS slot_name text NOT NULL DEFAULT '';

ALTER TABLE prompt_vault
  DROP CONSTRAINT IF EXISTS prompt_vault_slot_unique;

DROP INDEX IF EXISTS prompt_vault_slot_unique;

CREATE UNIQUE INDEX prompt_vault_slot_unique
  ON prompt_vault (category, vertical, platform, slot_name);

COMMENT ON COLUMN prompt_vault.slot_name IS
  'Nombre semántico del slot dentro de (category, vertical, platform). Permite variantes coexistir. Ejemplos: daily_special, weekend_event, before_after, behind_the_scenes.';
