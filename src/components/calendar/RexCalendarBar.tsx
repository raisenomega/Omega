import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useAutonomousMode } from "@/hooks/useAutonomousMode";
import { AutonomousModeToggle } from "@/components/calendar/AutonomousModeToggle";

// Tira COMPACTA de REX para la barra superior del Calendario · foto chica + 1 línea + acción.
// La LÓGICA es la misma (sin add-on → CTA "Activar REX" · con add-on → AutonomousModeToggle).
// Layout (C3): el contenedor crece (className sm:flex-1 desde el padre) y la acción se va sola
// al borde derecho (sm:ml-auto) · así el texto de REX queda al centro y el toggle a la derecha.
export function RexCalendarBar({ clientId, className }: { clientId: string; className?: string }) {
  const navigate = useNavigate();
  const { data, isLoading } = useAutonomousMode(clientId);
  const hasAddon = !!data?.rex_addon_active;

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <img src="/Agentes/Rex.jpg" alt="REX" className="h-7 w-7 rounded-md object-cover shrink-0" />
      <p className="hidden lg:block whitespace-nowrap text-xs text-muted-foreground">
        REX publica tus posts a su hora — solo los que apruebas
      </p>
      {!isLoading && (hasAddon ? (
        <span className="sm:ml-auto"><AutonomousModeToggle clientId={clientId} /></span>
      ) : (
        <Button size="sm" className="shrink-0 sm:ml-auto" onClick={() => navigate("/add-ons#rex")}>
          Activar REX
        </Button>
      ))}
    </div>
  );
}
