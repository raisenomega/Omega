// F.2 · Paso 1/2 · genera el guion estructurado del carrusel (backend A1.2 · tool_choice forzado).
// El `idea` viaja por su propio campo (max 4000) · NO el prompt de imagen. El front edita solo el `text`.
import { useMutation } from "@tanstack/react-query";
import { apiPost } from "@/lib/api-client";

export interface CarouselSlideData {
  order?: number | null;
  slide_type?: string | null;
  text: string;          // copy en la placa (español) · editable en el front
  visual_note: string;   // dirección de arte (inglés) · interno · NUNCA se muestra al usuario
}

export interface CarouselScript {
  carousel_title: string;
  slides: CarouselSlideData[];
}

export interface CarouselScriptInput {
  idea: string;
  clientId?: string;
  tone?: string;
}

export function useGenerateCarouselScript() {
  return useMutation<CarouselScript, Error, CarouselScriptInput>({
    mutationFn: ({ idea, clientId, tone }) =>
      apiPost<CarouselScript>("/content-lab/carousel-script", {
        idea, client_id: clientId || undefined, tone: tone || undefined,
      }),
  });
}
