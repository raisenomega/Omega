import { useQueryClient } from "@tanstack/react-query";
import { useGoogleProperties, useSetGoogleProperty } from "@/hooks/useGoogleProperties";
import { useToast } from "@/hooks/use-toast";

interface Props { clientId: string; connected: boolean; }

/** Picker de propiedad GA4 (Vía A · solo si Google está conectado). Lista las propiedades REALES del
 * cliente (accountSummaries) y persiste la elegida (external_account_id → habilita GA4 en el chip).
 * Honesto (P1): sin propiedades → mensaje claro, cero mock. White-label: "Google"/"Analytics". */
export function GooglePropertyPicker({ clientId, connected }: Props) {
  const { toast } = useToast();
  const qc = useQueryClient();
  const { data, isLoading } = useGoogleProperties(clientId, connected);
  const setProp = useSetGoogleProperty(clientId);

  if (!connected) return null;
  if (isLoading) return <p className="text-xs text-muted-foreground">Cargando tus propiedades de Analytics…</p>;
  const props = data?.properties ?? [];
  if (props.length === 0)
    return <p className="text-xs text-muted-foreground">No encontramos propiedades de Analytics en tu cuenta de Google.</p>;

  return (
    <select
      className="w-full rounded-md border border-border/40 bg-background p-1.5 text-xs"
      defaultValue=""
      disabled={setProp.isPending}
      onChange={(e) => {
        const pid = e.target.value;
        if (!pid) return;
        setProp.mutate(pid, {
          onSuccess: () => {
            toast({ title: "Propiedad de Analytics seleccionada" });
            qc.invalidateQueries({ queryKey: ["intelligence", "chip", "google"] });
          },
          onError: (err) => toast({ title: "No se pudo guardar", description: err.message, variant: "destructive" }),
        });
      }}
    >
      <option value="">Elegí tu propiedad de Analytics…</option>
      {props.map((p) => <option key={p.property_id} value={p.property_id}>{p.display_name}</option>)}
    </select>
  );
}
