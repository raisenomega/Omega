import { Sparkles, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  improvedText: string;
  onAccept: () => void;
  onReject: () => void;
}

export function ImprovePromptPanel({ improvedText, onAccept, onReject }: Props) {
  return (
    <div className="border-2 border-amber-400 bg-amber-50 dark:bg-amber-950/30 rounded-lg p-3 space-y-2">
      <div className="flex items-center gap-1.5 text-[11px] text-amber-700 dark:text-amber-300 font-medium">
        <Sparkles className="h-3.5 w-3.5" />
        ARIA sugiere esta versión mejorada:
      </div>
      <p className="text-xs text-foreground italic leading-relaxed">{improvedText}</p>
      <div className="flex gap-2 justify-end">
        <Button size="sm" variant="ghost" onClick={onReject} className="h-7 text-xs gap-1">
          <X className="h-3 w-3" /> Rechazar
        </Button>
        <Button size="sm" onClick={onAccept}
          className="h-7 text-xs gap-1 bg-amber-600 hover:bg-amber-700 text-white">
          <Check className="h-3 w-3" /> Aceptar
        </Button>
      </div>
    </div>
  );
}
