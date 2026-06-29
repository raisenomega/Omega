import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAutonomousMode } from "@/hooks/useAutonomousMode";
import { AutonomousModeToggle } from "@/components/calendar/AutonomousModeToggle";

// Tira COMPACTA de REX para la barra superior del Calendario (Commit 2 · antes era una Card
// estirada py-4). Foto chica + 1 línea + acción a la derecha. La LÓGICA es la misma:
//   - sin add-on → CTA "Activar REX" (→ /add-ons#rex · checkout Stripe real)
//   - con add-on → toggle Modo Autónomo (reusa AutonomousModeToggle · cero cambio)
// Solo cambió el tamaño/layout · el copy honesto (P1) se conserva en 1 línea.
export function RexCalendarBar({ clientId }: { clientId: string }) {
  const navigate = useNavigate();
  const { data, isLoading } = useAutonomousMode(clientId);
  const hasAddon = !!data?.rex_addon_active;

  return (
    <div className="flex items-center gap-2 sm:ml-auto">
      <img src="/Agentes/Rex.jpg" alt="REX" className="h-7 w-7 rounded-md object-cover shrink-0" />
      <p className="hidden lg:block whitespace-nowrap text-xs text-muted-foreground">
        REX publica tus posts a su hora — solo los que apruebas
      </p>
      {!isLoading && (hasAddon ? (
        <AutonomousModeToggle clientId={clientId} />
      ) : (
        <Button size="sm" className="shrink-0" onClick={() => navigate("/add-ons#rex")}>
          Activar REX
        </Button>
      ))}
    </div>
  );
}
