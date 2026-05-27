import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "./use-toast";
import { apiPost } from "@/lib/api-client";

interface ToggleResponse {
  success: boolean;
  auto_recharge: boolean;
}

// DEBT-052 F4: toggle de auto-recarga del credit pack (self-service · cliente por JWT).
// Invalida la query de créditos para reflejar el nuevo estado.
export function useAutoRechargeToggle(clientId: string) {
  const { toast } = useToast();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (enabled: boolean) =>
      apiPost<ToggleResponse>(`/billing/credits/auto-recharge`, { enabled }),
    onSuccess: (_d, enabled) => {
      qc.invalidateQueries({ queryKey: ["client_agent_credits", clientId] });
      toast({ title: enabled ? "Auto-recarga activada" : "Auto-recarga desactivada" });
    },
    onError: (e: Error) => {
      const notEnrolled = e.message.includes("not_enrolled") || e.message.includes("no_active_pack");
      toast({
        title: notEnrolled ? "Sin Credit Pack activo" : "No se pudo cambiar",
        description: notEnrolled ? "Activá un Credit Pack primero." : e.message,
        variant: "destructive",
      });
    },
  });
}
