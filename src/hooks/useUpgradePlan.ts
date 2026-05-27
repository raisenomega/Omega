import { useMutation } from "@tanstack/react-query";
import { useToast } from "./use-toast";
import { apiPost } from "@/lib/api-client";

/**
 * Upgrade plan via Stripe Checkout.
 *
 * Flow:
 * 1. POST /api/v1/billing/create-checkout-session con { client_id, target_plan }
 * 2. Backend (bc_billing) crea/reusa Stripe Customer + Checkout session
 * 3. Frontend redirige a `data.checkout_url` (hosted Stripe Checkout)
 * 4. Stripe redirect a STRIPE_SUCCESS_URL · webhook actualiza client_plans
 *
 * DEBT-CL-003 cerrada: usa apiPost (incluye Authorization Bearer automático ·
 * cierra bug latente del fetch raw que no mandaba auth · si backend valida
 * JWT → RBAC correcto · si lo ignora → sin cambio).
 *
 * Errors propagados como Error.message (api-client wrap):
 * - 503 price_not_configured: STRIPE_PRICE_* vacío en backend .env
 * - 400 invalid_upgrade_path: pro→basic, etc.
 * - 404 client_not_found: client_id no existe
 * - 500 stripe error: SDK falló
 */
interface UpgradePlanInput {
  clientId: string;
  targetPlan: "basic" | "pro" | "enterprise";
}

interface CheckoutResponse {
  checkout_url: string;
}

export function useUpgradePlan() {
  const { toast } = useToast();

  return useMutation({
    mutationFn: async ({ clientId, targetPlan }: UpgradePlanInput) => {
      const data = await apiPost<CheckoutResponse>(`/billing/create-checkout-session`, {
        client_id: clientId,
        target_plan: targetPlan,
      });
      if (!data.checkout_url) throw new Error("Sin checkout_url en respuesta backend");
      // External redirect a Stripe hosted (no SPA navigation)
      window.location.href = data.checkout_url;
    },
    onError: (e: Error) =>
      toast({
        title: "Upgrade no disponible",
        description: e.message,
        variant: "destructive",
      }),
  });
}
