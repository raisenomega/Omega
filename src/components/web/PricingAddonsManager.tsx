import { useState } from "react";
import { Plus, Pencil } from "lucide-react";
import { useAdminPricingAddons, type AddonDraft } from "@/hooks/useAdminPricingAddons";
import { PricingAddonDialog } from "./PricingAddonDialog";
import { ConfirmDeleteButton } from "./ConfirmDeleteButton";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";

// Editor CRUD de add-ons. Crear/editar (PricingAddonDialog) · eliminar con confirmación · toggle
// is_visible inline. Supabase directo (hook). price_suffix editable. SIN Stripe.
export function PricingAddonsManager() {
  const { addons, isLoading, save, remove, patch } = useAdminPricingAddons();
  const { toast } = useToast();
  const [editing, setEditing] = useState<AddonDraft | null>(null);
  const [open, setOpen] = useState(false);

  const onError = (e: unknown) =>
    toast({ title: "No se pudo guardar", description: e instanceof Error ? e.message : "Error", variant: "destructive" });

  const onSave = (s: AddonDraft) => save.mutate(s, { onSuccess: () => setOpen(false), onError });

  if (isLoading) return <Skeleton className="h-64 w-full" />;

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-lg font-bold text-foreground">Add-ons</h2>
        <Button size="sm" onClick={() => { setEditing(null); setOpen(true); }}><Plus className="mr-1 h-4 w-4" /> Nuevo</Button>
      </div>

      <div className="space-y-3">
        {addons.map((a) => (
          <Card key={a.id}>
            <CardHeader className="flex flex-row items-center justify-between gap-4 py-4">
              <div>
                <CardTitle className="text-sm font-medium">{a.name_es} / {a.name_en} · +${a.price}{a.price_suffix}</CardTitle>
                <p className="text-xs text-muted-foreground">orden {a.display_order}</p>
              </div>
              <div className="flex items-center gap-2">
                <Switch checked={a.is_visible} onCheckedChange={(v) => patch.mutate({ id: a.id, is_visible: v }, { onError })} />
                <Button variant="ghost" size="icon" onClick={() => { setEditing(a); setOpen(true); }}><Pencil className="h-4 w-4" /></Button>
                <ConfirmDeleteButton label={a.name_es} onConfirm={() => remove.mutate(a.id, { onError })} />
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>

      <PricingAddonDialog initial={editing} open={open} onOpenChange={setOpen} onSave={onSave} />
    </div>
  );
}
