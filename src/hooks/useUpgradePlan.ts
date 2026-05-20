import { useMutation } from "@tanstack/react-query";
import { useToast } from "./use-toast";

/**
 * Upgrade plan via Stripe Checkout.
 *
 * Flow:
 * 1. POST a /api/v1/billing/create-checkout-session con { client_id, target_plan }
 * 2. Backend (bc_billing) crea/reusa Stripe Customer + Checkout session
 * 3. Frontend redirige a `data.checkout_url` (hosted Stripe Checkout)
 * 4. Stripe redirect a STRIPE_SUCCESS_URL post-payment · webhook actualiza
 *    client_plans con período real
 *
 * Errors:
 * - 503 price_not_configured: STRIPE_PRICE_* vacío en backend .env
 * - 400 invalid_upgrade_path: pro→basic, etc.
 * - 404 client_not_found: client_id no existe
 * - 500 stripe error: SDK falló
 */
interface UpgradePlanInput {
  clientId: string;
  targetPlan: "basic" | "pro";
}

export function useUpgradePlan() {
  const { toast } = useToast();

  return useMutation({
    mutationFn: async ({ clientId, targetPlan }: UpgradePlanInput) => {
      const apiBase = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
      const res = await fetch(`${apiBase}/billing/create-checkout-session`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          client_id: clientId,
          target_plan: targetPlan,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        const detail = errData.detail;
        const errorMsg =
          typeof detail === "string"
            ? detail
            : detail?.error || `HTTP ${res.status}`;
        throw new Error(errorMsg);
      }

      const data = await res.json();
      if (!data.checkout_url) {
        throw new Error("Sin checkout_url en respuesta backend");
      }

      // Redirect a Stripe Checkout hosted (no SPA navigation · external URL)
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
