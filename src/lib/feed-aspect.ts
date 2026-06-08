// Rango de aspect ratio (w/h) que el FEED de Instagram acepta. AUTORIDAD: Instagram (no Zernio).
// DEBE coincidir con el backend (backend/app/api/routes/publishing/_media_guard.py · _FEED_RATIO_RULES
// ["instagram"]). Misma fuente, mismos numeros: si divergen, el aviso inline no calza con el rechazo real.
export const IG_FEED_RATIO_MIN = 0.8; // 4:5 vertical (limite inferior inclusive)
export const IG_FEED_RATIO_MAX = 1.91; // landscape (limite superior inclusive)

// Redes con feed de ratio acotado. instagram = feed restringido · tiktok/facebook/linkedin/twitter = lenientes.
export function feedRejectsRatio(platform: string, ratio: number): boolean {
  if (platform === "instagram") return !(ratio >= IG_FEED_RATIO_MIN && ratio <= IG_FEED_RATIO_MAX);
  return false;
}
