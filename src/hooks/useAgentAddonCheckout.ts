import { useMutation } from "@tanstack/react-query";
import { useToast } from "./use-toast";
import { useDemoMode } from "./useDemoMode";
import { apiPost } from "@/lib/api-client";

interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
}

interface CheckoutInput {
  agent_addon_code: string;
}

// DEBT-091: Stripe Checkout para Agent Add-On (Publicador/Creativo/Tendencias).
// Patrón espejo de useVideoPackCheckout. Backend valida JWT + plan pago + no-duplicado.
export function useAgentAddonCheckout() {
  const { toast } = useToast();
  const { isDemoAccount } = useDemoMode();
  return useMutation({
    mutationFn: async ({ agent_addon_code }: CheckoutInput) => {
      // Demo Mode: la cuenta demo NUNCA dispara Stripe real.
      if (isDemoAccount) {
        toast({ title: "Modo demo", description: "Los agentes no se cobran en la cuenta de demo." });
        return;
      }
      const data = await apiPost<CheckoutResponse>(
        `/billing/checkout-agent-addon`, { agent_addon_code },
      );
      if (!data.checkout_url) throw new Error("Sin checkout_url en respuesta backend");
      window.location.href = data.checkout_url;  // External Stripe redirect
    },
    onError: (e: Error) => {
      const msg = e.message;
      const title =
        msg.includes("already_active") ? "Ya tenés este agente activo"
        : msg.includes("requires_paid_plan") ? "Requiere plan pago"
        : msg.includes("price_not_configured") ? "Configuración pendiente"
        : "Agente no disponible";
      const description =
        msg.includes("already_active") ? "Gestioná tus agentes desde el Stripe Customer Portal."
        : msg.includes("requires_paid_plan") ? "Adopción no incluye agentes · actualizá tu plan primero."
        : msg.includes("price_not_configured") ? "Stripe del agente aún no configurado. Avisanos."
        : msg;
      toast({ title, description, variant: "destructive" });
    },
  });
}
