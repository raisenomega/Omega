import { Bot, Loader2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { useAutonomousMode, useSetAutonomousMode } from "@/hooks/useAutonomousMode";

// Toggle "Modo Autónomo (Rex)" · visible SOLO si el negocio compró el add-on
// (rex_addon_active). Off por defecto. Encender = consentimiento humano para que Rex
// publique solo lo ya aprobado, a su hora. El backend re-valida la compra al encender.
export function AutonomousModeToggle({ clientId }: { clientId: string }) {
  const { data, isLoading } = useAutonomousMode(clientId);
  const setMode = useSetAutonomousMode(clientId);

  if (isLoading || !data || !data.rex_addon_active) return null;

  return (
    <Card>
      <CardContent className="flex items-center justify-between gap-4 py-4">
        <div className="flex items-start gap-3">
          <Bot className="h-5 w-5 text-primary mt-0.5 shrink-0" />
          <div className="space-y-0.5">
            <p className="text-sm font-medium">Modo Autónomo (Rex)</p>
            <p className="text-xs text-muted-foreground">
              Rex publica automáticamente los posts que ya aprobaste, a su hora programada.
              Tú apruebas; Rex ejecuta. Apágalo cuando quieras.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {setMode.isPending && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
          <Switch
            checked={data.autonomous_mode_on}
            disabled={setMode.isPending}
            onCheckedChange={(v) => setMode.mutate(v)}
            aria-label="Modo Autónomo"
          />
        </div>
      </CardContent>
    </Card>
  );
}
