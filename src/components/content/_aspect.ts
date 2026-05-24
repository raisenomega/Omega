export const ASPECTS = ["1:1", "9:16", "16:9"] as const;
export type Aspect = typeof ASPECTS[number];
export const ASPECT_LABELS: Record<Aspect, string> = { "1:1": "Cuadrado", "9:16": "Story", "16:9": "Landscape" };
