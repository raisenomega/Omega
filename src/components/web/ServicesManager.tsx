import { useState } from "react";
import { Plus, Pencil } from "lucide-react";
import { useAdminServices, type ServiceDraft } from "@/hooks/useAdminServices";
import { ServiceEditDialog } from "./ServiceEditDialog";
import { ServiceDeleteButton } from "./ServiceDeleteButton";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";

// Editor CRUD de servicios (Sitio Web · owner-only). Crear/editar (ServiceEditDialog) · eliminar con
// confirmación (ServiceDeleteButton) · toggle is_visible inline. Escritura Supabase directo (hook).
export function ServicesManager() {
  const { services, isLoading, save, remove, patch } = useAdminServices();
  const { toast } = useToast();
  const [editing, setEditing] = useState<ServiceDraft | null>(null);
  const [open, setOpen] = useState(false);

  const onError = (e: unknown) =>
    toast({ title: "No se pudo guardar", description: e instanceof Error ? e.message : "Error", variant: "destructive" });

  const openNew = () => { setEditing(null); setOpen(true); };
  const openEdit = (s: ServiceDraft) => { setEditing(s); setOpen(true); };
  const onSave = (s: ServiceDraft) => save.mutate(s, { onSuccess: () => setOpen(false), onError });

  if (isLoading) return <Skeleton className="h-96 w-full" />;

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-foreground">Servicios</h1>
          <p className="text-sm text-muted-foreground">Tarjetas de la sección Servicios de la landing.</p>
        </div>
        <Button size="sm" onClick={openNew}><Plus className="mr-1 h-4 w-4" /> Nuevo</Button>
      </div>

      <div className="space-y-3">
        {services.map((s) => (
          <Card key={s.id}>
            <CardHeader className="flex flex-row items-center justify-between gap-4 py-4">
              <div>
                <CardTitle className="text-sm font-medium">{s.title_es} / {s.title_en}</CardTitle>
                <p className="text-xs text-muted-foreground">{s.icon} · orden {s.display_order}</p>
              </div>
              <div className="flex items-center gap-2">
                <Switch checked={s.is_visible} onCheckedChange={(v) => patch.mutate({ id: s.id, is_visible: v }, { onError })} />
                <Button variant="ghost" size="icon" onClick={() => openEdit(s)}><Pencil className="h-4 w-4" /></Button>
                <ServiceDeleteButton title={s.title_es} onConfirm={() => remove.mutate(s.id, { onError })} />
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>

      <ServiceEditDialog initial={editing} open={open} onOpenChange={setOpen} onSave={onSave} />
    </div>
  );
}
