import type { ReactNode } from "react";
import { Loader2, AlertCircle, Lightbulb } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

// Bloque de estado de la pagina Estrategias (extraido en C.2 para no romper el ratchet C4 de
// Strategies.tsx): loading → spinner · error → reintentar · vacio → empty honesto · si no → la grilla.
export function StrategiesGrid({ loading, isError, empty, emptyTitle, emptyMsg, onRetry, children }: {
  loading: boolean; isError: boolean; empty: boolean; emptyTitle: string; emptyMsg: string;
  onRetry: () => void; children: ReactNode;
}) {
  if (loading) {
    return <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>;
  }
  if (isError) {
    return (
      <Card><CardContent className="flex flex-col items-center gap-3 py-10 text-center">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <p className="text-sm font-medium">No se pudieron cargar las estrategias</p>
        <Button size="sm" variant="outline" onClick={onRetry}>Reintentar</Button>
      </CardContent></Card>
    );
  }
  if (empty) {
    return (
      <Card><CardContent className="flex flex-col items-center gap-3 py-10 text-center">
        <Lightbulb className="h-10 w-10 text-muted-foreground/30" />
        <p className="text-sm font-medium">{emptyTitle}</p>
        <p className="text-xs text-muted-foreground">{emptyMsg}</p>
      </CardContent></Card>
    );
  }
  return <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">{children}</div>;
}
