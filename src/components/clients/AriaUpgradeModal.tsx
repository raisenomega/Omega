import { ArrowUpRight, Check, Sparkles } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { apiPost } from "@/lib/api-client";
import { ARIA_LEVELS, ariaLevelInfo } from "@/lib/aria-levels";

// P1 (cero precio falso): el backend /billing/upgrade-aria cobra UN addon plano (+1 nivel)
// al price Stripe configurado (representado como $12, igual que ARIAUpgradeBanner). Por eso el
// modal muestra SOLO el próximo nivel con ESE precio real · nunca un precio que Stripe no cobra.
// Precios por-nivel distintos ($25/$49) + salto directo = DEBT-094 (3 productos Stripe + target_level).
const ARIA_NEXT_PRICE = "$12/mes";

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

  const nextLevel = currentLevel + 1;
  const atMax = currentLevel >= 4;
  const next = atMax ? null : ARIA_LEVELS[nextLevel];

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-1">
          Mejorar modelo ARIA <ArrowUpRight className="h-3.5 w-3.5" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-amber-500" /> Mejorar ARIA
          </DialogTitle>
        </DialogHeader>
        <p className="text-xs text-muted-foreground">
          Tu nivel actual: <span className="font-medium text-foreground">{ariaLevelInfo(currentLevel).label}</span>
        </p>
        {atMax || !next ? (
          <p className="py-4 text-center text-sm text-muted-foreground">Estás en el nivel máximo de ARIA.</p>
        ) : (
          <>
            <div className="rounded-lg border border-amber-500 bg-amber-500/5 p-3">
              <div className="flex items-center justify-between gap-2">
                <Badge className={next.color}>{next.label}</Badge>
                <span className="text-sm font-semibold">{ARIA_NEXT_PRICE}</span>
              </div>
              <p className="mt-1.5 text-xs text-muted-foreground">{next.desc}</p>
              <ul className="mt-2 space-y-1">
                {next.benefits.map((b) => (
                  <li key={b} className="flex gap-1.5 text-[11px] text-muted-foreground">
                    <Check className="mt-0.5 h-3 w-3 shrink-0 text-emerald-600" />{b}
                  </li>
                ))}
              </ul>
            </div>
            <Button
              onClick={() => m.mutate()}
              disabled={m.isPending}
              className="w-full border border-amber-500 bg-transparent text-white transition-colors duration-200 hover:bg-emerald-600 hover:border-emerald-600 hover:text-white"
            >
              {m.isPending ? "Redirigiendo a Stripe…" : `Actualizar a ARIA ${nextLevel}.0 · ${ARIA_NEXT_PRICE}`}
            </Button>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
