/** Helpers puros del flujo de conexión OAuth-por-red (B-2). Sin render → testeable.
 * White-label: la etiqueta cara-cliente es el NOMBRE DE LA RED (nunca "Zernio"). */

export const PLATFORM_LABELS: Record<string, string> = {
  instagram: "Instagram",
  facebook: "Facebook",
  tiktok: "TikTok",
  twitter: "X / Twitter",
  linkedin: "LinkedIn",
  youtube: "YouTube",
};

export function platformLabel(platform: string): string {
  return PLATFORM_LABELS[platform] ?? platform;
}

export interface ConnectedItem {
  platform: string;
  handle: string | null;
  zernio_account_id: string;
  followers_count?: number | null;   // real de Zernio (connected-accounts) · null/ausente → '—'
}

/** ¿La red está conectada (aparece en el profile del negocio)? Lee la verdad real, no el @handle. */
export function isConnected(platform: string, items: ConnectedItem[]): boolean {
  return items.some((i) => i.platform === platform);
}

/** Seguidores REALES de la red conectada (de connected-accounts · Zernio en vivo, no persistido).
 * null si la red no está conectada o no hay dato → la fila muestra '—', JAMÁS 0 inventado (P1). */
export function accountFollowers(platform: string, items: ConnectedItem[]): number | null {
  const it = items.find((i) => i.platform === platform);
  return it && typeof it.followers_count === "number" ? it.followers_count : null;
}

/** ¿Todas las redes del negocio están conectadas? (apaga el parpadeo del tab cuando es true). */
export function allConnected(platforms: string[], items: ConnectedItem[]): boolean {
  return platforms.length > 0 && platforms.every((p) => isConnected(p, items));
}

export type ConnectState = "connected" | "awaiting" | "connect";

/** Estado HONESTO del botón (P1): el verde 'connected' SOLO sale de la verdad de Zernio
 * (`connected`, del GET connected-accounts). Abrir el popup (`awaitingVerify`) jamás significa
 * conectado — ofrece verificar/reintentar, nunca afirma el hecho. */
export function connectButtonState(connected: boolean, awaitingVerify: boolean): ConnectState {
  if (connected) return "connected";
  return awaitingVerify ? "awaiting" : "connect";
}
