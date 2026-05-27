import { useState } from "react";
import { Check, Coins } from "lucide-react";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useCreditPackCheckout, type CreditPackCode } from "@/hooks/useCreditPackCheckout";

interface CreditPackInfo {
  code: CreditPackCode;
  name: string;
  price: string;
  tagline: string;
  bullets: readonly string[];
}

// DEBT-052 · modal de selección de Credit Pack (4 opciones · estilo espejo de AriaUpgradeModal).
// Card seleccionable (useState · sin pre-selección) + botón dinámico → useCreditPackCheckout → Stripe.
const CREDIT_PACKS: readonly CreditPackInfo[] = [
  {
    code: "micro",
    name: "Micro",
    price: "$9",
    tagline: "Para uso ocasional",
    bullets: ["~180 generaciones de texto", "~180 imágenes extra", "Auto-recarga: opcional"],
  },
  {
    code: "starter",
    name: "Starter",
    price: "$25",
    tagline: "Para uso activo",
    bullets: ["~500 generaciones de texto", "~500 imágenes extra", "Auto-recarga: opcional"],
  },
  {
    code: "plus",
    name: "Plus",
    price: "$59",
    tagline: "Para uso intensivo",
    bullets: ["~1,200 generaciones de texto", "~1,200 imágenes extra", "Auto-recarga: recomendada"],
  },
  {
    code: "ultra",
    name: "Ultra",
    price: "$119",
    tagline: "Para agencias y power users",
    bullets: ["~2,400 generaciones de texto", "~2,400 imágenes extra", "Auto-recarga: activada por defecto"],
  },
];

export function CreditPackModal() {
  const checkout = useCreditPackCheckout();
  const [selected, setSelected] = useState<CreditPackCode | null>(null);

  const chosen = CREDIT_PACKS.find((p) => p.code === selected) ?? null;

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          size="sm"
          className="w-full border border-amber-500 bg-transparent text-white transition-colors duration-200 hover:bg-emerald-600 hover:border-emerald-600 hover:text-white"
        >
          Añadir Créditos
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Coins className="h-4 w-4 text-amber-500" /> Añade Créditos por tu consumo
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-2">
          {CREDIT_PACKS.map((p) => {
            const isSelected = p.code === selected;
            return (
              <button
                key={p.code}
                type="button"
                onClick={() => setSelected(p.code)}
                className={`w-full rounded-lg border p-3 text-left transition-colors ${
                  isSelected ? "border-amber-500 bg-amber-500/5" : "border-border/40 hover:border-border"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium">
                    {p.name} <span className="text-muted-foreground font-normal">{p.price}/mes</span>
                  </span>
                  {isSelected && <span className="text-[10px] font-medium text-amber-500">Seleccionado</span>}
                </div>
                <p className="mt-1.5 text-xs text-muted-foreground">{p.tagline}</p>
                <ul className="mt-2 space-y-1">
                  {p.bullets.map((b) => (
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
          onClick={() => { if (chosen) checkout.mutate({ credit_pack_code: chosen.code }); }}
          disabled={!chosen || checkout.isPending}
          className="w-full border border-amber-500 bg-transparent text-white transition-colors duration-200 hover:bg-emerald-600 hover:border-emerald-600 hover:text-white"
        >
          {checkout.isPending
            ? "Redirigiendo a Stripe…"
            : chosen
              ? `Comprar ${chosen.name} · ${chosen.price}/mes`
              : "Seleccioná un pack"}
        </Button>
      </DialogContent>
    </Dialog>
  );
}
