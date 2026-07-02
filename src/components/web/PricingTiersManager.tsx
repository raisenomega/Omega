import { useState } from "react";
import { Plus, Pencil } from "lucide-react";
import { useAdminPricingTiers, type TierDraft } from "@/hooks/useAdminPricingTiers";
import { PricingTierDialog } from "./PricingTierDialog";
import { ConfirmDeleteButton } from "./ConfirmDeleteButton";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";

// Editor CRUD de planes (tiers). Crear/editar (PricingTierDialog) · eliminar con confirmación ·
// toggle is_visible inline. Supabase directo (hook). SIN Stripe.
export function PricingTiersManager() {
  const { tiers, isLoading, save, remove, patch } = useAdminPricingTiers();
  const { toast } = useToast();
  const [editing, setEditing] = useState<TierDraft | null>(null);
  const [open, setOpen] = useState(false);

  const onError = (e: unknown) =>
    toast({ title: "No se pudo guardar", description: e instanceof Error ? e.message : "Error", variant: "destructive" });

  const onSave = (s: TierDraft) => save.mutate(s, { onSuccess: () => setOpen(false), onError });

  if (isLoading) return <Skeleton className="h-64 w-full" />;

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-lg font-bold text-foreground">Planes</h2>
        <Button size="sm" onClick={() => { setEditing(null); setOpen(true); }}><Plus className="mr-1 h-4 w-4" /> Nuevo</Button>
      </div>

      <div className="space-y-3">
        {tiers.map((t) => (
          <Card key={t.id}>
            <CardHeader className="flex flex-row items-center justify-between gap-4 py-4">
              <div>
                <CardTitle className="text-sm font-medium">
                  {t.name_es} / {t.name_en} · ${t.price}{t.is_recommended ? " · ★ Recomendado" : ""}
                </CardTitle>
                <p className="text-xs text-muted-foreground">orden {t.display_order}</p>
              </div>
              <div className="flex items-center gap-2">
                <Switch checked={t.is_visible} onCheckedChange={(v) => patch.mutate({ id: t.id, is_visible: v }, { onError })} />
                <Button variant="ghost" size="icon" onClick={() => { setEditing(t); setOpen(true); }}><Pencil className="h-4 w-4" /></Button>
                <ConfirmDeleteButton label={t.name_es} onConfirm={() => remove.mutate(t.id, { onError })} />
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>

      <PricingTierDialog initial={editing} open={open} onOpenChange={setOpen} onSave={onSave} />
    </div>
  );
}
