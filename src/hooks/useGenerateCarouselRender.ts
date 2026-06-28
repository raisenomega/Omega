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
}

export interface CarouselRenderInput {
  carouselTitle: string;
  slides: CarouselSlideData[];
  clientId?: string;
}

export function useGenerateCarouselRender() {
  return useMutation<CarouselRenderResult, Error, CarouselRenderInput>({
    mutationFn: ({ carouselTitle, slides, clientId }) =>
      apiPost<CarouselRenderResult>("/content-lab/carousel-render", {
        carousel_title: carouselTitle, slides, client_id: clientId || undefined,
      }),
  });
}
