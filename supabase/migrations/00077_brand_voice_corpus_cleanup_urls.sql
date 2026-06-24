-- ╔═══════════════════════════════════════════════════════════════════╗
-- ║  Migración 00077 · limpieza brand_voice_corpus · borra filas-URL      ║
-- ║  24 jun 2026 · raíz del score X5 bajo a todo (referencia envenenada)  ║
-- ║                                                                   ║
-- ║  Causa (sonda v2): drafts content_type=image guardan la URL de la    ║
-- ║  imagen en generated_text (no hay caption). Al aprobar, esa URL       ║
-- ║  entraba a brand_voice_corpus → fetch_recent_corpus tomaba URLs como  ║
-- ║  "ejemplos_aprobados" → el scorer Haiku medía cada caption contra     ║
-- ║  URLs → score bajo a TODO el negocio (Zafacones 0.45/0.15 vs Mail     ║
-- ║  Boxes 0.78+ con corpus sano).                                       ║
-- ║                                                                   ║
-- ║  La escritura ya quedó blindada en código (is_corpus_worthy_text ·    ║
-- ║  rechaza URLs/vacío en TODOS los paths de insert). Esta migración     ║
-- ║  SANEA lo ya contaminado · GLOBAL (todos los negocios, no solo el     ║
-- ║  de raisen@) · solo filas cuyo text ES una URL (empieza con http://   ║
-- ║  o https://). NUNCA toca captions de texto reales (una URL DENTRO de  ║
-- ║  un caption no empieza con http → no matchea).                       ║
-- ║  Idempotente (re-correr borra 0). 19 filas al momento de escribir     ║
-- ║  (5a323aa3×1, 7663aa55×3, afb9f578×10, b8d1b9f5×5 · todas             ║
-- ║  source=approved_draft).                                            ║
-- ╚═══════════════════════════════════════════════════════════════════╝

-- ─── Borrar SOLO filas cuyo text es una URL (image URL envenenada) ───
-- ILIKE anclado al inicio: 'http://%' / 'https://%'. Una URL en medio de un
-- caption real NO empieza con http → se conserva. No filtra por source (cubre
-- cualquier origen que haya metido una URL · approved_draft o futuro).
DELETE FROM brand_voice_corpus
WHERE text ILIKE 'http://%'
   OR text ILIKE 'https://%';

-- ═══════════════════════════════════════════════════════════════════
-- Verificación post-apply (manual · NO ejecuta acá):
--   -- Cero filas-URL en TODO el corpus:
--   SELECT count(*) FROM brand_voice_corpus
--   WHERE text ILIKE 'http://%' OR text ILIKE 'https://%';   -- esperado: 0
--
--   -- Corpus sano por negocio (ejemplos = captions reales, no URLs):
--   SELECT client_id, count(*), min(left(text,40)) AS muestra
--   FROM brand_voice_corpus GROUP BY client_id ORDER BY count(*) DESC;
-- ═══════════════════════════════════════════════════════════════════
-- FIN MIGRACIÓN 00077
