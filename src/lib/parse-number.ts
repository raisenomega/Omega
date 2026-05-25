// FIX 2: convierte texto con separadores (comas, puntos, espacios) a número.
// "10,000" → 10000 · "1.500" → 1500 · El usuario escribe formato libre y se guarda el número.
// null si queda vacío o no es numérico.
export function parseLooseNumber(raw: string): number | null {
  const cleaned = raw.replace(/[,.\s]/g, "");
  if (!cleaned) return null;
  const n = Number(cleaned);
  return Number.isFinite(n) ? n : null;
}
