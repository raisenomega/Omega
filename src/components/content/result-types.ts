// Tipos compartidos de Content Lab results · split de ResultCardV2 (C4)

export interface ResultV2 {
  id: string;
  generated_text: string;
  content_type: string;
  variation_label?: string;
  virality_score?: number;
  virality_estimated?: boolean;
  brand_dna_score?: number;
  saved?: boolean;
  is_story?: boolean;  // Pieza 3 · foto 9:16 marcada para historia (default undefined = post normal · retrocompat)
  status?: "pending" | "completed" | "failed";
  // Brave Search · content_type='research' usa estos campos en lugar de generated_text
  url?: string;
  snippet?: string;
  title?: string;
}

export type ModalState = "closed" | "open" | "minimized";
export interface BlockState { items: ResultV2[] }
