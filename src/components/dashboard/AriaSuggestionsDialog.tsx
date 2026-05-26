import { X } from "lucide-react";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ARIASuggestion } from "@/hooks/useAriaSuggestions";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  suggestions: ARIASuggestion[];
  onMarkRead: (id: string) => void;
}

// Historial completo de sugerencias de ARIA · leídas tachadas/gris (P1 · empty honesto)
export function AriaSuggestionsDialog({ open, onOpenChange, suggestions, onMarkRead }: Props) {
  const ordered = [...suggestions].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Sugerencias de ARIA</DialogTitle>
          <DialogDescription>Historial completo de recomendaciones.</DialogDescription>
        </DialogHeader>
        {ordered.length === 0 ? (
          <p className="text-xs text-muted-foreground py-4">ARIA todavía no generó sugerencias.</p>
        ) : (
          <ScrollArea className="max-h-[60vh] pr-3">
            <ul className="space-y-2">
              {ordered.map((s) => (
                <li key={s.id} className="flex items-start justify-between gap-2 text-xs border-b border-border/40 pb-2">
                  <span className={s.is_read ? "line-through text-muted-foreground" : "text-foreground"}>
                    {s.message}
                  </span>
                  {!s.is_read && (
                    <Button variant="ghost" size="icon" className="h-5 w-5 shrink-0"
                      onClick={() => onMarkRead(s.id)} aria-label="Marcar como leída">
                      <X className="h-3.5 w-3.5" />
                    </Button>
                  )}
                </li>
              ))}
            </ul>
          </ScrollArea>
        )}
      </DialogContent>
    </Dialog>
  );
}
