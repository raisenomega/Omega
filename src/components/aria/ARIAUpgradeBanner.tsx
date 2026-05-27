import { ArrowUpRight, Loader2 } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { apiPost } from "@/lib/api-client";

// Banner upgrade ARIA Premium · DEBT-037 V1 cerrada (cliente · $12/mes)
// Reseller variant pending DEBT-046.
// DEBT-CL-003 cerrada: usa apiPost en vez de fetch raw + supabase.auth directo.

interface ARIAUpgradeBannerProps {
  currentLevel: number;
}

const startAriaUpgrade = (): Promise<{ checkout_url: string; session_id: string }> =>
  apiPost<{ checkout_url: string; session_id: string }>(`/billing/upgrade-aria`, {});

export function ARIAUpgradeBanner({ currentLevel }: ARIAUpgradeBannerProps) {
  const { toast } = useToast();
  const targetLevel = currentLevel + 1;
  const m = useMutation({
    mutationFn: startAriaUpgrade,
    onSuccess: (r) => { window.location.href = r.checkout_url; },
    onError: (e: Error) => {
      const isActive = e.message.includes("already_active");
      const isUnconfig = e.message.includes("price_not_configured");
      toast({
        title: isActive ? "ARIA Premium ya activo" : isUnconfig ? "Configuración pendiente" : "No se pudo iniciar",
        description: isActive ? "Ya tenés ARIA Premium en tu cuenta." : isUnconfig ? "Stripe ARIA Premium aún no está configurado. Avisanos." : e.message,
        variant: isActive ? "default" : "destructive",
      });
    },
  });

  if (currentLevel === 1 || currentLevel >= 4) return null;

  return (
    <div className="border-t border-border bg-muted/30 px-3 py-2 flex items-center justify-between gap-2">
      <span className="text-xs text-muted-foreground">
        Actualizar a ARIA {targetLevel}.0 — $12/mes
      </span>
      <Button
        size="sm"
        variant="outline"
        onClick={() => m.mutate()}
        disabled={m.isPending}
        className="h-7 gap-1 text-xs"
      >
        {m.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <ArrowUpRight className="h-3 w-3" />}
        {m.isPending ? "Iniciando…" : "Actualizar"}
      </Button>
    </div>
  );
}
