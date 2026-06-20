import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAutonomousMode } from "@/hooks/useAutonomousMode";
import { AutonomousModeToggle } from "@/components/calendar/AutonomousModeToggle";

// Barra de descubrimiento de REX en el Calendario · visible para TODOS (compren o no · todos los planes).
// Copy HONESTO (P1): solo "publica a su hora" es presente (lo que el E2E verificó · lo que activa el
// add-on) · el resto de la visión es "Próximamente", sin prometerlo como activo.
// Dos estados según rex_addon_active:
//   - sin add-on → CTA "Activar REX" (→ /add-ons · checkout Stripe real de Esencial/Pro)
//   - con add-on → toggle Modo Autónomo (usar · reusa AutonomousModeToggle)
// Foto REAL de REX (la misma del add-on), no un icono genérico.
export function RexCalendarBar({ clientId }: { clientId: string }) {
  const navigate = useNavigate();
  const { data, isLoading } = useAutonomousMode(clientId);
  const hasAddon = !!data?.rex_addon_active;

  return (
    <Card className="border-primary/30 bg-primary/5">
      <CardContent className="flex items-center gap-4 py-4">
        <img
          src="/Agentes/Rex.jpg"
          alt="REX"
          className="h-14 w-14 rounded-lg object-cover shrink-0"
        />
        <div className="flex-1 space-y-0.5 min-w-0">
          <p className="text-sm font-semibold">
            REX publica tus posts automáticamente a su hora — solo los que tú apruebas
          </p>
          <p className="text-xs text-muted-foreground">
            Próximamente: planificación semanal, mejor horario, reportes y más.
          </p>
        </div>
        {!isLoading && (hasAddon ? (
          <AutonomousModeToggle clientId={clientId} />
        ) : (
          <Button size="sm" className="shrink-0" onClick={() => navigate("/add-ons")}>
            Activar REX
          </Button>
        ))}
      </CardContent>
    </Card>
  );
}
