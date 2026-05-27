import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "./use-toast";
import { useDemoMode } from "./useDemoMode";
import { apiPost } from "@/lib/api-client";

interface ScheduleDowngradeInput {
  clientId: string;
  targetPlan: "basic" | "pro";
}

/**
 * DEBT-076 · Programa un downgrade a fin de ciclo (Stripe SubscriptionSchedule).
 *
 * NO es un checkout (no redirige a Stripe) · el cambio se aplica solo al
 * current_period_end y el webhook customer.subscription.updated sincroniza el plan.
 *
 * Errores propagados como Error.message (api-client wrap):
 * - 503 price_not_configured: STRIPE_PRICE_<plan> vacío en backend .env
 * - 400 invalid_downgrade_path · 409 no_active_subscription · 403 access_denied
 */
export function useScheduleDowngrade(onDone?: () => void) {
  const { toast } = useToast();
  const { isDemoAccount } = useDemoMode();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ clientId, targetPlan }: ScheduleDowngradeInput) => {
      if (isDemoAccount) {
        toast({ title: "Modo demo", description: 'Cambiá el plan con el toggle "Vista" del menú de usuario · sin cobro.' });
        return;
      }
      await apiPost<{ success: boolean }>(`/billing/schedule-downgrade`, {
        client_id: clientId,
        target_plan: targetPlan,
      });
    },
    onSuccess: () => {
      toast({ title: "Downgrade programado", description: "El cambio se aplicará al final de tu ciclo actual." });
      queryClient.invalidateQueries({ queryKey: ["client_plans"] });
      onDone?.();
    },
    onError: (e: Error) =>
      toast({ title: "No se pudo programar el cambio", description: e.message, variant: "destructive" }),
  });
}
