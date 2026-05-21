import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface WizardFooterProps {
  activeIndex: number;
  totalSections: number;
  isLast: boolean;
  canSubmit: boolean;
  isSubmitting: boolean;
  isEditing?: boolean;
  onPrev: () => void;
  onNext: () => void;
  onSubmit: () => void;
}

export function WizardFooter({
  activeIndex, totalSections, isLast,
  canSubmit, isSubmitting, isEditing, onPrev, onNext, onSubmit,
}: WizardFooterProps) {
  const submittingLabel = isEditing ? "Guardando…" : "Creando…";
  const submitLabel = isEditing ? "Guardar Cambios" : "Crear Cliente";
  return (
    <div className="border-t border-border bg-background px-4 py-3 flex items-center gap-3">
      <Button
        variant="outline"
        onClick={onPrev}
        disabled={activeIndex === 0}
        className="gap-1"
      >
        <ChevronLeft className="h-4 w-4" />
        Anterior
      </Button>

      <div className="flex-1 text-center text-xs text-muted-foreground tabular-nums">
        Sección {activeIndex + 1} de {totalSections}
      </div>

      {isLast ? (
        <Button
          onClick={onSubmit}
          disabled={!canSubmit}
          title={canSubmit ? "" : "Completa nombre, industria y región"}
        >
          {isSubmitting ? submittingLabel : submitLabel}
        </Button>
      ) : (
        <Button onClick={onNext} className="gap-1">
          Siguiente
          <ChevronRight className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}
