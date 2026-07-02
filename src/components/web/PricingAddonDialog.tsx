import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import type { AddonDraft } from "@/hooks/useAdminPricingAddons";

const EMPTY: AddonDraft = {
  name_es: "", name_en: "", description_es: "", description_en: "",
  price: 0, price_suffix: "/mes", is_visible: true, display_order: 0,
};

interface Props {
  initial: AddonDraft | null;
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onSave: (s: AddonDraft) => void;
}

// Formulario crear/editar add-on. Bilingüe. price_suffix editable ("/mes" · col 00088). SIN
// stripe_price_id (el checkout va aparte). Switch Visible.
export function PricingAddonDialog({ initial, open, onOpenChange, onSave }: Props) {
  const [draft, setDraft] = useState<AddonDraft>(EMPTY);
  useEffect(() => setDraft(initial ?? EMPTY), [initial, open]);
  const set = (p: Partial<AddonDraft>) => setDraft((d) => ({ ...d, ...p }));

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] max-w-lg overflow-auto">
        <DialogHeader>
          <DialogTitle>{draft.id ? "Editar" : "Nuevo"} add-on</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Nombre (ES)</Label><Input value={draft.name_es} onChange={(e) => set({ name_es: e.target.value })} /></div>
            <div><Label>Nombre (EN)</Label><Input value={draft.name_en} onChange={(e) => set({ name_en: e.target.value })} /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Descripción (ES)</Label><Textarea rows={2} value={draft.description_es} onChange={(e) => set({ description_es: e.target.value })} /></div>
            <div><Label>Descripción (EN)</Label><Textarea rows={2} value={draft.description_en} onChange={(e) => set({ description_en: e.target.value })} /></div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div><Label>Precio (USD)</Label><Input type="number" value={draft.price} onChange={(e) => set({ price: Number(e.target.value) })} /></div>
            <div><Label>Sufijo</Label><Input value={draft.price_suffix} onChange={(e) => set({ price_suffix: e.target.value })} /></div>
            <div><Label>Orden</Label><Input type="number" value={draft.display_order} onChange={(e) => set({ display_order: Number(e.target.value) })} /></div>
          </div>
          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <Switch checked={draft.is_visible} onCheckedChange={(v) => set({ is_visible: v })} /> Visible en la landing
          </label>
          <Button className="w-full" onClick={() => onSave(draft)}>Guardar</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
