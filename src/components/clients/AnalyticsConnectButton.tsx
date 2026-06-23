import { Button } from "@/components/ui/button";
import { Loader2, Link2, CheckCircle2 } from "lucide-react";

interface Props { label: string; sublabel: string; connected: boolean; isPending: boolean; onConnect: () => void; }

/** Vista pura del conector de analítica (Google/Meta). Calco visual de ZernioConnectButton:
 * ✓ verde si conectado · botón pulse-amber "Conectar {label}" si no. HONESTIDAD (P1): el verde
 * sale del status REAL (prop connected · /oauth/{provider}/status), NUNCA de abrir el popup. */
export function AnalyticsConnectButton({ label, sublabel, connected, isPending, onConnect }: Props) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg border border-border/30 bg-muted/20 p-2.5">
      <div className="min-w-0">
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs text-muted-foreground">{sublabel}</p>
      </div>
      {connected ? (
        <span className="flex items-center gap-1 text-xs text-success shrink-0">
          <CheckCircle2 className="h-3.5 w-3.5" />Conectado
        </span>
      ) : (
        <Button variant="outline" size="sm"
                className="h-7 text-xs shrink-0 animate-pulse border-amber-500/60 text-amber-600"
                disabled={isPending} onClick={onConnect}>
          {isPending ? <Loader2 className="mr-1 h-3 w-3 animate-spin" /> : <Link2 className="mr-1 h-3 w-3" />}
          {`Conectar ${label}`}
        </Button>
      )}
    </div>
  );
}
