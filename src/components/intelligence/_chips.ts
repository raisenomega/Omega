export type ChipId = "resumen" | "seo" | "geo" | "aeo" | "meta" | "google";

export interface Chip {
  id: ChipId;
  label: string;
}

export const INTELLIGENCE_CHIPS: readonly Chip[] = [
  { id: "resumen", label: "Resumen" },
  { id: "seo",     label: "SEO" },
  { id: "geo",     label: "GEO" },
  { id: "aeo",     label: "AEO" },
  { id: "meta",    label: "Meta" },
  { id: "google",  label: "Google" },
];
