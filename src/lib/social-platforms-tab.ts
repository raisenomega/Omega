/** Fuente ÚNICA de plataformas del TAB CUENTAS de ARIA (NO el modal de 10 secciones).
 * 3 capas que NO deben desincronizarse: (1) este archivo · (2) el CHECK de
 * social_accounts.platform (migr 00071) · (3) el onboarding §7 (subset intencional · 6 sin
 * reddit). Si Reddit/coming-soon cambian, los tres se actualizan juntos. Ver
 * DEBT-PLATFORMS-PINTEREST-SNAPCHAT-THREADS-BLUESKY en ESTADO_OMEGA. */

export interface TabPlatform {
  value: string;
  label: string;
}

/** Conectables vía OAuth Zernio (botón "Vincular"). Casan 1:1 con el CHECK de la DB (migr
 * 00071). Reddit incluido: Zernio da authUrl y el connect del backend es genérico
 * (get_connect_url no tiene allowlist). El onboarding §7 queda en 6 a propósito (no se toca). */
export const CONNECTABLE_PLATFORMS: TabPlatform[] = [
  { value: "instagram", label: "Instagram" },
  { value: "facebook", label: "Facebook" },
  { value: "tiktok", label: "TikTok" },
  { value: "twitter", label: "X / Twitter" },
  { value: "linkedin", label: "LinkedIn" },
  { value: "youtube", label: "YouTube" },
  { value: "reddit", label: "Reddit" },
];

/** Próximamente · INFORMATIVAS, no accionables (sin botón · gris · NO se insertan en
 * social_accounts → no necesitan estar en el CHECK todavía). Zernio aún no las sirve
 * conectables: threads/bluesky sin authUrl prioritario · pinterest=503 (caída temporal) ·
 * snapchat=403 (beta). GATILLO de habilitación: cuando Zernio devuelva 200+authUrl →
 * re-sondear → mover a CONNECTABLE_PLATFORMS + agregar al CHECK (nueva migración). */
export const COMING_SOON_PLATFORMS: TabPlatform[] = [
  { value: "threads", label: "Threads" },
  { value: "bluesky", label: "Bluesky" },
  { value: "pinterest", label: "Pinterest" },
  { value: "snapchat", label: "Snapchat" },
];

/** Leyenda cara-cliente del tab · nombra el universo conectable real + la regla de negocio
 * (una cuenta por red por negocio · a propósito, no es un límite). */
export const TAB_PLATFORMS_LEGEND =
  "Redes conectables: Instagram, Facebook, TikTok, X / Twitter, LinkedIn, YouTube y Reddit. " +
  "Una cuenta por red por negocio (para publicar de forma eficiente y efectiva).";
