import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { SERVICE_ICON_NAMES } from "@/components/landing/service-icons";
import type { ServiceDraft } from "@/hooks/useAdminServices";

const EMPTY: ServiceDraft = {
  icon: "Target", title_es: "", title_en: "", description_es: "", description_en: "",
  benefits_es: [], benefits_en: [], display_order: 0, is_visible: true,
};

interface Props {
  initial: ServiceDraft | null;
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onSave: (s: ServiceDraft) => void;
}

// Formulario crear/editar servicio (bilingüe). Beneficios uno-por-línea (join/split \n · el hook
// limpia vacíos). Ícono desde el set único lucide. is_visible como Switch (gana el molde: se oculta
// sin borrar). El estado local se resetea cada vez que cambia `initial`/`open`.
export function ServiceEditDialog({ initial, open, onOpenChange, onSave }: Props) {
  const [draft, setDraft] = useState<ServiceDraft>(EMPTY);
  useEffect(() => setDraft(initial ?? EMPTY), [initial, open]);
  const set = (p: Partial<ServiceDraft>) => setDraft((d) => ({ ...d, ...p }));

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] max-w-lg overflow-auto">
        <DialogHeader>
          <DialogTitle>{draft.id ? "Editar" : "Nuevo"} servicio</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Título (ES)</Label><Input value={draft.title_es} onChange={(e) => set({ title_es: e.target.value })} /></div>
            <div><Label>Título (EN)</Label><Input value={draft.title_en} onChange={(e) => set({ title_en: e.target.value })} /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>Ícono</Label>
              <Select value={draft.icon} onValueChange={(v) => set({ icon: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {SERVICE_ICON_NAMES.map((n) => <SelectItem key={n} value={n}>{n}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div><Label>Orden</Label><Input type="number" value={draft.display_order} onChange={(e) => set({ display_order: Number(e.target.value) })} /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Descripción (ES)</Label><Textarea rows={2} value={draft.description_es} onChange={(e) => set({ description_es: e.target.value })} /></div>
            <div><Label>Descripción (EN)</Label><Textarea rows={2} value={draft.description_en} onChange={(e) => set({ description_en: e.target.value })} /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Beneficios ES (uno por línea)</Label><Textarea rows={3} value={draft.benefits_es.join("\n")} onChange={(e) => set({ benefits_es: e.target.value.split("\n") })} /></div>
            <div><Label>Beneficios EN (uno por línea)</Label><Textarea rows={3} value={draft.benefits_en.join("\n")} onChange={(e) => set({ benefits_en: e.target.value.split("\n") })} /></div>
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
