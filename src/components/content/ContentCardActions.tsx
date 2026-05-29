import { Check, X, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { ContentItem } from "@/hooks/useContentActions";
import { useSaveContent, useReuseContent } from "@/hooks/useContentActions";

interface ContentCardActionsProps {
  item: ContentItem;
  reuseMode?: boolean;
}

// Footer de acciones de la tarjeta de contenido. reuseMode (tab Papelera) muestra solo "Reusar"
// (rejected → borrador). El borrado [x] NO existe aún (endpoint pendiente) → ausente, no mock.
export function ContentCardActions({ item, reuseMode = false }: ContentCardActionsProps) {
  const save = useSaveContent();
  const reuse = useReuseContent();

  if (reuseMode) {
    return (
      <div className="flex gap-2 pt-1">
        <Button
          size="sm"
          variant="outline"
          className="gap-1 h-8 flex-1"
          disabled={reuse.isPending}
          onClick={() => reuse.mutate(item.id)}
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Reusar
        </Button>
      </div>
    );
  }

  return (
    <div className="flex gap-2 pt-1">
      <Button
        size="sm"
        variant={item.is_saved ? "default" : "outline"}
        className={`gap-1 h-8 flex-1 ${item.is_saved ? "bg-emerald-600 hover:bg-emerald-700" : ""}`}
        disabled={save.isPending}
        onClick={() => save.mutate({ id: item.id, is_saved: !item.is_saved })}
      >
        <Check className="h-3.5 w-3.5" />
        {item.is_saved ? "Guardado" : "Guardar"}
      </Button>
      {item.is_saved && (
        <Button
          size="sm"
          variant="ghost"
          className="gap-1 h-8"
          disabled={save.isPending}
          onClick={() => save.mutate({ id: item.id, is_saved: false })}
        >
          <X className="h-3.5 w-3.5" />Descartar
        </Button>
      )}
    </div>
  );
}
