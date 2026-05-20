import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useARIA } from "@/contexts/ARIAContext";
import { useARIAChat } from "@/hooks/useARIAChat";

// ARIAButton · global en AppHeader · siempre visible
// Texto "ARIA X.0" con icono Sparkles Lucide (NO emojis)
// Dot pulsante azul como indicador activo · click abre drawer

export function ARIAButton() {
  const { openARIA } = useARIA();
  const { ariaLevel } = useARIAChat();

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={openARIA}
      className="relative h-9 gap-1.5 px-2.5"
      aria-label={`Abrir ARIA ${ariaLevel}.0`}
    >
      <span className="text-xs font-semibold tabular-nums">ARIA {ariaLevel}.0</span>
      <Sparkles className="h-3.5 w-3.5" />
      <span className="absolute -top-0.5 -right-0.5 h-2 w-2 rounded-full bg-primary animate-pulse" />
    </Button>
  );
}
