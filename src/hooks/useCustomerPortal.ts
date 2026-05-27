import { useMutation } from "@tanstack/react-query";
import { useToast } from "./use-toast";
import { apiPost } from "@/lib/api-client";

interface PortalResponse {
  portal_url: string;
}

// DEBT-038: Stripe Customer Portal · el cliente gestiona su suscripción
// (método de pago, cancelar, facturas) en el portal hosteado de Stripe.
// Patrón espejo de useVideoPackCheckout. Backend valida JWT + stripe_customer_id.
export function useCustomerPortal() {
  const { toast } = useToast();
  return useMutation({
    mutationFn: async () => {
      const data = await apiPost<PortalResponse>(`/billing/customer-portal`, {});
      if (!data.portal_url) throw new Error("Sin portal_url en respuesta backend");
      window.location.href = data.portal_url;  // External Stripe redirect
    },
    onError: (e: Error) => {
      const msg = e.message;
      const title =
        msg.includes("no_stripe_customer") ? "Sin suscripción activa"
        : msg.includes("stripe_not_configured") ? "Configuración pendiente"
        : "Gestión no disponible";
      const description =
        msg.includes("no_stripe_customer") ? "Activá un plan primero para poder gestionar tu suscripción."
        : msg.includes("stripe_not_configured") ? "Stripe aún no está configurado. Avisanos."
        : msg;
      toast({ title, description, variant: "destructive" });
    },
  });
}
