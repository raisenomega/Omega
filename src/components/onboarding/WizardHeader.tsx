import { X } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";

interface WizardHeaderProps {
  completionPercent: number;
  isEditing?: boolean;
  onClose?: () => void;
}

function completionColor(pct: number): string {
  if (pct >= 80) return "text-emerald-600";
  if (pct >= 40) return "text-amber-600";
  return "text-rose-600";
}

export function WizardHeader({ completionPercent, isEditing, onClose }: WizardHeaderProps) {
  return (
    <div className="border-b border-border bg-background/95 px-4 py-3 backdrop-blur sticky top-0 z-10">
      <div className="flex items-center justify-between gap-3 mb-2">
        <h2 className="text-lg font-semibold">{isEditing ? "Editar Cliente" : "Nuevo Cliente"}</h2>
        <div className="flex items-center gap-3">
          <span className={`text-sm font-medium tabular-nums ${completionColor(completionPercent)}`}>
            {completionPercent}%
          </span>
          {onClose && (
            <Button size="icon" variant="ghost" onClick={onClose} aria-label="Cerrar">
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
      <Progress value={completionPercent} className="h-1.5 transition-all" />
      <p className="text-xs text-muted-foreground mt-1">
        Has completado {completionPercent}% · Recomendamos 80% para que ARIA opere mejor desde el primer día
      </p>
    </div>
  );
}
