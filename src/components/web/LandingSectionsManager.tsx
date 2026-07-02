import { useAdminLandingSections } from "@/hooks/useAdminLandingSections";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";

// Réplica adaptada del AdminSections del molde. El landing_sections de OMEGA solo tiene
// visibilidad + orden (las columnas de texto/servicios/footer llegan en rebanadas siguientes),
// así que en esta rebanada la UI se limita a esos dos controles por sección.
const LABELS: Record<string, string> = {
  hero: "Hero / Inicio",
  pain_solution: "Dolor / Solución",
  services: "Servicios",
  social_proof: "Prueba Social",
  process: "Proceso",
  lead_form: "Formulario de Leads",
};

export function LandingSectionsManager() {
  const { sections, isLoading, patch } = useAdminLandingSections();
  const { toast } = useToast();

  const onError = (e: unknown) =>
    toast({
      title: "No se pudo guardar",
      description: e instanceof Error ? e.message : "Error desconocido",
      variant: "destructive",
    });

  if (isLoading) return <Skeleton className="h-96 w-full" />;

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-2 font-display text-2xl font-bold text-foreground">Secciones de la Landing</h1>
      <p className="mb-8 text-sm text-muted-foreground">
        Activá o desactivá cada sección de la página pública y ajustá su orden de aparición.
      </p>

      <div className="space-y-3">
        {sections.map((s) => (
          <Card key={s.id}>
            <CardHeader className="flex flex-row items-center justify-between gap-4 py-4">
              <CardTitle className="text-sm font-medium">{LABELS[s.name] ?? s.name}</CardTitle>
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 text-xs text-muted-foreground">
                  Orden
                  <Input
                    type="number"
                    defaultValue={s.display_order}
                    className="h-8 w-16"
                    onBlur={(e) => {
                      const v = Number(e.target.value);
                      if (Number.isFinite(v) && v !== s.display_order)
                        patch.mutate({ id: s.id, display_order: v }, { onError });
                    }}
                  />
                </label>
                <Switch
                  checked={s.is_visible}
                  onCheckedChange={(v) => patch.mutate({ id: s.id, is_visible: v }, { onError })}
                />
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>
    </div>
  );
}
