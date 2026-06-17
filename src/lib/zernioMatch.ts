/** Lógica pura de coincidencia de handles para el picker de binding Zernio.
 * Separada del componente para testearla sin render (anti-cross-publish: el auto-match
 * y el warning de mismatch dependen de esto). normaliza @, mayúsculas y espacios. */

export interface ZernioOption {
  zernio_account_id: string;
  platform: string;
  handle: string | null;
}

export function normalizeHandle(s: string | null | undefined): string {
  return (s ?? "").trim().toLowerCase().replace(/^@+/, "").replace(/\s+/g, "");
}

/** Dos handles "coinciden" si, normalizados, son iguales y no vacíos. */
export function handlesMatch(a: string | null | undefined, b: string | null | undefined): boolean {
  const na = normalizeHandle(a);
  return na.length > 0 && na === normalizeHandle(b);
}

/** Pre-selección: la opción Zernio cuyo handle coincide con el del negocio. null si ninguna
 * (fuerza elección manual + warning) o si hay >1 coincidencia (ambiguo → no adivinar). */
export function autoMatch(options: ZernioOption[], accountName: string | null | undefined): ZernioOption | null {
  const hits = options.filter((o) => handlesMatch(o.handle, accountName));
  return hits.length === 1 ? hits[0] : null;
}
