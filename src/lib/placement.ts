// AMBAS · helpers de placement (feed/story/both) compartidos en el front.
// Espejo de backend _fanout._placement_variants + _publish_service._STORY_PLATFORMS:
// DEBE coincidir con esos (misma fuente de verdad · igual que feed-aspect.ts ↔ _media_guard.py).
export type Placement = "feed" | "story" | "both";

// Redes que soportan historia (IG/FB). El resto: "both" = solo feed (no hay historia donde ponerla).
export const STORY_NETWORKS = new Set(["instagram", "facebook"]);

// Cuántas publicaciones genera un placement en UNA red (= filas que emite _fanout para esa red):
// feed→1 · story→1 · both→ 1 feed + (1 historia SOLO si la red soporta story).
export function placementPubCount(placement: Placement, network: string): number {
  if (placement === "both") return 1 + (STORY_NETWORKS.has(network) ? 1 : 0);
  return 1;  // feed | story → 1 publicación
}
