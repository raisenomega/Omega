import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import type { TierDraft } from "@/hooks/useAdminPricingTiers";

const EMPTY: TierDraft = {
  name_es: "", name_en: "", tagline_es: "", tagline_en: "", price: 0,
  features_es: [], features_en: [], is_recommended: false, is_visible: true, display_order: 0,
};

interface Props {
  initial: TierDraft | null;
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onSave: (s: TierDraft) => void;
}

// Formulario crear/editar plan (tier). Bilingüe. Features uno-por-línea (el hook limpia vacíos).
// SIN stripe_price_id (el checkout va aparte). Switches Recomendado + Visible.
export function PricingTierDialog({ initial, open, onOpenChange, onSave }: Props) {
  const [draft, setDraft] = useState<TierDraft>(EMPTY);
  useEffect(() => setDraft(initial ?? EMPTY), [initial, open]);
  const set = (p: Partial<TierDraft>) => setDraft((d) => ({ ...d, ...p }));

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] max-w-lg overflow-auto">
        <DialogHeader>
          <DialogTitle>{draft.id ? "Editar" : "Nuevo"} plan</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Nombre (ES)</Label><Input value={draft.name_es} onChange={(e) => set({ name_es: e.target.value })} /></div>
            <div><Label>Nombre (EN)</Label><Input value={draft.name_en} onChange={(e) => set({ name_en: e.target.value })} /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Tagline (ES)</Label><Input value={draft.tagline_es} onChange={(e) => set({ tagline_es: e.target.value })} /></div>
            <div><Label>Tagline (EN)</Label><Input value={draft.tagline_en} onChange={(e) => set({ tagline_en: e.target.value })} /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Precio (USD)</Label><Input type="number" value={draft.price} onChange={(e) => set({ price: Number(e.target.value) })} /></div>
            <div><Label>Orden</Label><Input type="number" value={draft.display_order} onChange={(e) => set({ display_order: Number(e.target.value) })} /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Features ES (uno por línea)</Label><Textarea rows={4} value={draft.features_es.join("\n")} onChange={(e) => set({ features_es: e.target.value.split("\n") })} /></div>
            <div><Label>Features EN (uno por línea)</Label><Textarea rows={4} value={draft.features_en.join("\n")} onChange={(e) => set({ features_en: e.target.value.split("\n") })} /></div>
          </div>
          <div className="flex items-center gap-6 text-sm text-muted-foreground">
            <label className="flex items-center gap-2"><Switch checked={draft.is_recommended} onCheckedChange={(v) => set({ is_recommended: v })} /> Recomendado</label>
            <label className="flex items-center gap-2"><Switch checked={draft.is_visible} onCheckedChange={(v) => set({ is_visible: v })} /> Visible</label>
          </div>
          <Button className="w-full" onClick={() => onSave(draft)}>Guardar</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
