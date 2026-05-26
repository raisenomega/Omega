import { useState } from "react";
import { Sparkles, Check, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAriaSuggestions, useMarkSuggestionRead } from "@/hooks/useAriaSuggestions";
import { AriaSuggestionsDialog } from "./AriaSuggestionsDialog";

interface Props {
  clientId: string | null;
}

// ARIA · sugerencias proactivas (últimas 3 no-leídas · empty honesto P1 · historial en dialog)
export function AriaSuggestionsCard({ clientId }: Props) {
  const { suggestions, unread, isLoading } = useAriaSuggestions(clientId);
  const markRead = useMarkSuggestionRead();
  const [open, setOpen] = useState(false);
  const top = unread.slice(0, 3);

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">Sugerencias de ARIA</CardTitle>
        <Sparkles className="h-4 w-4 text-primary" />
      </CardHeader>
      <CardContent className="space-y-3">
        {!clientId ? (
          <p className="text-xs text-muted-foreground">Seleccioná un cliente para ver sus sugerencias.</p>
        ) : isLoading ? (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Loader2 className="h-3 w-3 animate-spin" />Cargando…
          </div>
        ) : top.length === 0 ? (
          <p className="text-xs text-muted-foreground">ARIA no tiene sugerencias nuevas.</p>
        ) : (
          <ul className="space-y-2">
            {top.map((s) => (
              <li key={s.id} className="flex items-start justify-between gap-2 text-xs">
                <span className="text-foreground">{s.message}</span>
                <Button variant="ghost" size="icon" className="h-5 w-5 shrink-0"
                  onClick={() => markRead.mutate(s.id)} disabled={markRead.isPending}
                  aria-label="Marcar como leída">
                  <Check className="h-3.5 w-3.5" />
                </Button>
              </li>
            ))}
          </ul>
        )}
        {clientId && (
          <Button variant="link" size="sm" className="h-auto p-0 text-xs"
            onClick={() => setOpen(true)}>
            Ver historial completo →
          </Button>
        )}
      </CardContent>
      <AriaSuggestionsDialog open={open} onOpenChange={setOpen}
        suggestions={suggestions} onMarkRead={(id) => markRead.mutate(id)} />
    </Card>
  );
}
