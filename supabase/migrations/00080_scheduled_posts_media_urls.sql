-- Pieza 2 · carrusel publicable · array de N media por fila · 26 jun 2026.
-- scheduled_posts.media_url (text · singular · 00020) solo lleva 1 imagen. Esta columna guarda el
-- carrusel completo. El publicador (capa 2 · commit aparte) cae a [media_url] cuando media_urls es NULL.
-- Forward-only · aditivo · CERO backfill: las filas previas a 00080 quedan NULL a propósito (el
-- fallback en código las maneja). Retrocompat total: nullable · sin DEFAULT · comportamiento de hoy intacto.
ALTER TABLE scheduled_posts
  ADD COLUMN IF NOT EXISTS media_urls text[];

COMMENT ON COLUMN scheduled_posts.media_urls IS
  'Carrusel: array de N media (Pieza 2). NULL en filas previas a 00080 → el publicador cae a [media_url] (fallback retrocompat). media_url se mantiene poblado con media_urls[0] por doble-escritura.';
