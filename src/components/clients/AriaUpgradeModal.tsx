import { useState } from "react";
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

// Precio mensual por nivel (display-only · el backend cobra +1 nivel a un precio Stripe fijo).
const ARIA_LEVEL_PRICE: Record<number, number> = { 2: 12, 3: 25, 4: 49 };

// Modal selector de niveles de ARIA · cada card es seleccionable · "Comprar" → Stripe checkout
// (POST /billing/upgrade-aria · mismo patrón que ARIAUpgradeBanner · +1 nivel por addon).
export function AriaUpgradeModal({ currentLevel }: { currentLevel: number }) {
  const { toast } = useToast();
  const [selected, setSelected] = useState<number | null>(null);
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

  // Nivel 1 (Adopción) es base · no comprable. Sólo 2/3/4 tienen precio.
  const isPurchasable = (lvl: number): boolean => lvl >= 2;
  const price = selected !== null ? ARIA_LEVEL_PRICE[selected] : undefined;

  const buttonLabel = (() => {
    if (m.isPending) return "Redirigiendo a Stripe…";
    if (selected === null) return "Seleccioná un nivel";
    if (selected === currentLevel) return "Ya tenés este nivel";
    if (!isPurchasable(selected)) return "Nivel base";
    return `Comprar ARIA ${selected}.0 · $${price}/mes`;
  })();

  const buttonDisabled =
    m.isPending ||
    selected === null ||
    selected === currentLevel ||
    !isPurchasable(selected);

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
            const isSelected = lvl === selected;
            return (
              <button
                key={lvl}
                type="button"
                onClick={() => setSelected(lvl)}
                className={`w-full rounded-lg border p-3 text-left transition-colors duration-200 ${
                  isSelected ? "border-amber-500 bg-amber-500/5" : "border-border/40 hover:border-border"
                }`}
              >
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
              </button>
            );
          })}
        </div>
        <Button
          onClick={() => m.mutate()}
          disabled={buttonDisabled}
          className="w-full border border-amber-500 bg-transparent text-white transition-colors duration-200 hover:bg-emerald-600 hover:border-emerald-600 hover:text-white"
        >
          {buttonLabel}
        </Button>
      </DialogContent>
    </Dialog>
  );
}
