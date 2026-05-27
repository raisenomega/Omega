import { ArrowUpRight, Check, Sparkles } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { apiPost } from "@/lib/api-client";
import { ARIA_LEVELS } from "@/lib/aria-levels";

const ARIA_STEP_PRICE = "$12/mes";

// Modal con los 4 niveles de ARIA + beneficios · "Actualizar" → Stripe checkout
// (POST /billing/upgrade-aria · mismo patrón que ARIAUpgradeBanner · +1 nivel por addon).
export function AriaUpgradeModal({ currentLevel }: { currentLevel: number }) {
  const { toast } = useToast();
  const m = useMutation({
    mutationFn: () => apiPost<{ checkout_url: string }>(`/billing/upgrade-aria`, {}),
    onSuccess: (r) => { window.location.href = r.checkout_url; },
    onError: (e: Error) => {
      const isActive = e.message.includes("already_active");
      const isUnconfig = e.message.includes("price_not_configured");
      toast({
        title: isActive ? "ARIA Premium ya activo" : isUnconfig ? "Configuración pendiente" : "No se pudo iniciar",
        description: isActive ? "Ya tenés este nivel activo." : isUnconfig ? "Stripe ARIA aún no configurado. Avisanos." : e.message,
        variant: isActive ? "default" : "destructive",
      });
    },
  });

  const nextLevel = Math.min(currentLevel + 1, 4);
  const canUpgrade = currentLevel < 4;

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-1">
          Mejorar modelo ARIA <ArrowUpRight className="h-3.5 w-3.5" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-amber-500" /> Niveles de ARIA
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-2">
          {[1, 2, 3, 4].map((lvl) => {
            const info = ARIA_LEVELS[lvl];
            const isCurrent = lvl === currentLevel;
            return (
              <div key={lvl} className={`rounded-lg border p-3 ${isCurrent ? "border-primary bg-primary/5" : "border-border/40"}`}>
                <div className="flex items-center justify-between gap-2">
                  <Badge className={info.color}>{info.label}</Badge>
                  {isCurrent && <span className="text-[10px] font-medium text-primary">Nivel actual</span>}
                </div>
                <p className="mt-1.5 text-xs text-muted-foreground">{info.desc}</p>
                <ul className="mt-2 space-y-1">
                  {info.benefits.map((b) => (
                    <li key={b} className="flex gap-1.5 text-[11px] text-muted-foreground">
                      <Check className="mt-0.5 h-3 w-3 shrink-0 text-emerald-600" />{b}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
        {canUpgrade ? (
          <Button
            onClick={() => m.mutate()}
            disabled={m.isPending}
            className="w-full border border-amber-500 bg-transparent text-white transition-colors duration-200 hover:bg-emerald-600 hover:border-emerald-600 hover:text-white"
          >
            {m.isPending ? "Redirigiendo a Stripe…" : `Actualizar a ARIA ${nextLevel}.0 · +${ARIA_STEP_PRICE}`}
          </Button>
        ) : (
          <p className="text-center text-xs text-muted-foreground">Estás en el nivel máximo de ARIA.</p>
        )}
      </DialogContent>
    </Dialog>
  );
}
