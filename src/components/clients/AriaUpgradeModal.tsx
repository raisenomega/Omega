import { ArrowUpRight, Check, Sparkles } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip, TooltipContent, TooltipProvider, TooltipTrigger,
} from "@/components/ui/tooltip";
import { useToast } from "@/hooks/use-toast";
import { apiPost } from "@/lib/api-client";
import { ARIA_LEVELS, ariaLevelInfo } from "@/lib/aria-levels";

// P1 (cero precio falso): el backend /billing/upgrade-aria cobra UN addon plano (+1 nivel)
// al price Stripe configurado (representado como $12, igual que ARIAUpgradeBanner). Por eso el
// modal muestra SOLO el próximo nivel con ESE precio real · nunca un precio que Stripe no cobra.
// Precios por-nivel distintos ($25/$49) + salto directo = DEBT-094 (3 productos Stripe + target_level).
const ARIA_NEXT_PRICE = "$12/mes";

// Copy de tooltip por nivel (hover sobre el chip). El label viene de ARIA_LEVELS (fuente única).
const ARIA_CHIP_TOOLTIP: Record<number, string> = {
  1: "Conversacional básico · onboarding y respuestas FAQ. Incluido en tu plan.",
  2: "Sugerencias de contenido + análisis simple de tu marca. +$12/mes",
  3: "NBA engine · predice tu mejor próxima acción + auto-publicación con aprobación. Disponible desde ARIA 2.0",
  4: "Contexto extendido · acciones autónomas con guardrails · análisis profundo de audiencia. Disponible desde ARIA 3.0",
};

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
        <Button
          size="sm"
          className="gap-1 border border-amber-500 bg-transparent text-white transition-colors duration-200 hover:bg-emerald-600 hover:border-emerald-600 hover:text-white"
        >
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
        <TooltipProvider>
          <div className="flex flex-wrap gap-1.5">
            {[1, 2, 3, 4].map((lvl) => {
              const isCurrent = lvl === currentLevel;
              return (
                <Tooltip key={lvl}>
                  <TooltipTrigger asChild>
                    <button
                      type="button"
                      className={`rounded-full px-2 py-1 text-[10px] font-medium transition-colors ${
                        isCurrent ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {ARIA_LEVELS[lvl].label}
                    </button>
                  </TooltipTrigger>
                  <TooltipContent side="top" className="max-w-[16rem] text-xs">
                    {ARIA_CHIP_TOOLTIP[lvl]}
                  </TooltipContent>
                </Tooltip>
              );
            })}
          </div>
        </TooltipProvider>
        {atMax || !next ? (
          <p className="py-4 text-center text-sm text-muted-foreground">Estás en el nivel máximo · ARIA 4.0</p>
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
