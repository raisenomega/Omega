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
  placement?: "feed" | "story" | "both";  // AMBAS · feed=post normal · story=historia · both=feed+historia (default undefined = "feed")
  media_urls?: string[];  // Carrusel (Pieza 1 · F.1) · N placas. generated_text = título/caption del carrusel.
  status?: "pending" | "completed" | "failed";
  // Brave Search · content_type='research' usa estos campos en lugar de generated_text
  url?: string;
  snippet?: string;
  title?: string;
}

export type ModalState = "closed" | "open" | "minimized";
export interface BlockState { items: ResultV2[] }
