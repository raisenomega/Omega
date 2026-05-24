import { useMutation } from "@tanstack/react-query";
import { useToast } from "./use-toast";
import { apiPost } from "@/lib/api-client";
import type { VideoPackCode } from "@/components/addons/_video_packs_data";

interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
}

interface CheckoutInput {
  video_pack_code: VideoPackCode;
}

// DEBT-VID-001: Stripe Checkout para Video Pack addon (Starter $39 ·
// Creator $95 · Cinematic Pro $125). Patrón espejo de useUpgradePlan.
// Backend valida JWT + plan basic/pro + 1 pack-a-la-vez.
export function useVideoPackCheckout() {
  const { toast } = useToast();
  return useMutation({
    mutationFn: async ({ video_pack_code }: CheckoutInput) => {
      const data = await apiPost<CheckoutResponse>(
        `/billing/checkout-video-pack`, { video_pack_code },
      );
      if (!data.checkout_url) throw new Error("Sin checkout_url en respuesta backend");
      window.location.href = data.checkout_url;  // External Stripe redirect
    },
    onError: (e: Error) => {
      const msg = e.message;
      const title =
        msg.includes("already_active") ? "Ya tenés un Video Pack activo"
        : msg.includes("requires_paid_plan") ? "Requiere plan Básico o PRO"
        : msg.includes("price_not_configured") ? "Configuración pendiente"
        : "Video Pack no disponible";
      const description =
        msg.includes("already_active") ? "Cancelá el actual desde Stripe Customer Portal para cambiar."
        : msg.includes("requires_paid_plan") ? "Adopción no incluye Video Packs · actualizá tu plan primero."
        : msg.includes("price_not_configured") ? "Stripe Video Pack aún no configurado. Avisanos."
        : msg;
      toast({ title, description, variant: "destructive" });
    },
  });
}
