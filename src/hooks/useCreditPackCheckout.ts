import { useMutation } from "@tanstack/react-query";
import { useToast } from "./use-toast";
import { apiPost } from "@/lib/api-client";

interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
}

export type CreditPackCode = "micro" | "starter" | "plus" | "ultra";

interface CheckoutInput {
  credit_pack_code: CreditPackCode;
}

// DEBT-052: Stripe Checkout para Credit Pack (Micro $9 · Starter $25 · Plus $59 · Ultra $119).
// Patrón espejo de useVideoPackCheckout. Backend valida JWT + plan pago + 1 pack-a-la-vez.
export function useCreditPackCheckout() {
  const { toast } = useToast();
  return useMutation({
    mutationFn: async ({ credit_pack_code }: CheckoutInput) => {
      const data = await apiPost<CheckoutResponse>(
        `/billing/checkout-credit-pack`, { credit_pack_code },
      );
      if (!data.checkout_url) throw new Error("Sin checkout_url en respuesta backend");
      window.location.href = data.checkout_url;  // External Stripe redirect
    },
    onError: (e: Error) => {
      const msg = e.message;
      const title =
        msg.includes("already_active") ? "Ya tenés un Credit Pack activo"
        : msg.includes("requires_paid_plan") ? "Requiere plan pago"
        : msg.includes("price_not_configured") ? "Configuración pendiente"
        : "Credit Pack no disponible";
      const description =
        msg.includes("already_active") ? "Cancelá el actual desde el portal de Stripe para cambiar."
        : msg.includes("requires_paid_plan") ? "Los Credit Packs requieren un plan pago (basic/pro/enterprise)."
        : msg.includes("price_not_configured") ? "Stripe del Credit Pack aún no configurado. Avisanos."
        : msg;
      toast({ title, description, variant: "destructive" });
    },
  });
}
