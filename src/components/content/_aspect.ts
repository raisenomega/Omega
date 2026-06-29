export const ASPECTS = ["1:1", "4:5", "9:16", "16:9"] as const;
export type Aspect = typeof ASPECTS[number];
export const ASPECT_LABELS: Record<Aspect, string> = { "1:1": "Cuadrado", "4:5": "vertical", "9:16": "Story", "16:9": "Landscape" };
