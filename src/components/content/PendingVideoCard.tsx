import { Loader2, X } from "lucide-react";
import { Card } from "@/components/ui/card";

interface Props {
  resultId: string;
  onCancel?: (id: string) => void;
}

// DEBT-CL-010: placeholder card mientras Veo genera el video (~30-90s).
// onCancel opcional · si presente muestra botón "Cancelar" esquina sup-derecha.
export function PendingVideoCard({ resultId, onCancel }: Props) {
  return (
    <Card className="relative h-full border-amber-500/30 flex flex-col items-center justify-center gap-2 p-4">
      {onCancel && (
        <button onClick={() => onCancel(resultId)}
          className="absolute top-1.5 right-1.5 h-6 px-2 rounded-md flex items-center gap-1 text-[10px] text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition"
          aria-label="Cancelar video">
          <X className="h-3 w-3" /> Cancelar
        </button>
      )}
      <Loader2 className="h-6 w-6 animate-spin text-amber-500" />
      <p className="text-xs text-center text-muted-foreground">ARIA está generando tu video...</p>
      <p className="text-[10px] text-center text-muted-foreground/60">~30-90 segundos</p>
    </Card>
  );
}
