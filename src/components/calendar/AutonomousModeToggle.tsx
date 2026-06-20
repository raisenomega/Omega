import { Loader2 } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { useAutonomousMode, useSetAutonomousMode } from "@/hooks/useAutonomousMode";

// Control compacto del Modo Autónomo (REX) · se usa DENTRO de RexCalendarBar (estado "ya comprado").
// Solo aparece si el negocio compró el add-on (rex_addon_active). Off por defecto · enciende
// autonomous_mode_on = consentimiento humano para que REX publique solo lo ya aprobado, a su hora.
export function AutonomousModeToggle({ clientId }: { clientId: string }) {
  const { data } = useAutonomousMode(clientId);
  const setMode = useSetAutonomousMode(clientId);

  if (!data || !data.rex_addon_active) return null;

  return (
    <div className="flex items-center gap-2 shrink-0">
      <span className="text-xs font-medium">Modo Autónomo</span>
      {setMode.isPending && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
      <Switch
        checked={data.autonomous_mode_on}
        disabled={setMode.isPending}
        onCheckedChange={(v) => setMode.mutate(v)}
        aria-label="Modo Autónomo"
      />
    </div>
  );
}
