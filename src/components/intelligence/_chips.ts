export type ChipId = "resumen" | "seo" | "geo" | "aeo" | "google";

export interface Chip {
  id: ChipId;
  label: string;
}

export const INTELLIGENCE_CHIPS: readonly Chip[] = [
  { id: "resumen", label: "Resumen" },
  { id: "seo",     label: "SEO" },
  { id: "geo",     label: "GEO" },
  { id: "aeo",     label: "AEO" },
  { id: "google",  label: "Google" },
];
