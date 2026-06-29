// F.2 · Paso 2/2 · renderiza el guion EDITADO a N placas reales (backend A2.4 · ~10s · todo-o-nada).
// Manda el guion editado (no el original) · el backend ensambla cada visual_note + marca y genera las placas.
import { useMutation } from "@tanstack/react-query";
import { apiPost } from "@/lib/api-client";
import type { CarouselSlideData } from "./useGenerateCarouselScript";

export interface CarouselRenderResult {
  id: string;
  content_type: string;   // "carousel"
  carousel_title: string;
  media_urls: string[];   // N URLs de las placas
  virality_score?: number;       // Commit 5b · chip "XX/100" (paridad caption)
  virality_estimated?: boolean;  // Commit 5b · chip "Estimado"
  brand_dna_score?: number;      // Commit 5b · chip "% voz de marca"
}

export interface CarouselRenderInput {
  carouselTitle: string;
  slides: CarouselSlideData[];
  clientId?: string;
  applyLogo?: boolean;  // Commit A · opt-in · overlay del logo sobre las N placas (default sin logo)
}

export function useGenerateCarouselRender() {
  return useMutation<CarouselRenderResult, Error, CarouselRenderInput>({
    mutationFn: ({ carouselTitle, slides, clientId, applyLogo }) =>
      apiPost<CarouselRenderResult>("/content-lab/carousel-render", {
        carousel_title: carouselTitle, slides, client_id: clientId || undefined,
        apply_logo: !!applyLogo,
      }),
  });
}
