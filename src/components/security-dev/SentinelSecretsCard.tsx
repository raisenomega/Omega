import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { useSecretsRotationStatus, useRegisterRotation, type RotationUrgency } from "@/hooks/useSecretsRotation";
import { fmtDateTime } from "./parts";

const URGENCY_CLS: Record<RotationUrgency, string> = {
  ok: "bg-green-500/15 text-green-500 border-green-500/40",
  warn: "bg-amber-500/15 text-amber-500 border-amber-500/40",
  urgent: "bg-red-500/15 text-red-500 border-red-500/40",
  baseline_unknown: "bg-muted/40 text-muted-foreground border-border/40",
};
const URGENCY_LABEL: Record<RotationUrgency, string> = {
  ok: "ok", warn: "rotar pronto", urgent: "rotar ya", baseline_unknown: "baseline desconocido",
};

export function SentinelSecretsCard() {
  const { data, isLoading } = useSecretsRotationStatus();
  const register = useRegisterRotation();
  const [confirm, setConfirm] = useState<string | null>(null);
  const secrets = data?.secrets ?? [];

  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Rotación de secrets</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {isLoading && <Skeleton className="h-24 w-full" />}
        {!isLoading && secrets.length === 0 && (
          <p className="text-xs text-muted-foreground">Sin secrets monitoreados.</p>
        )}
        {secrets.map((s) => (
          <div key={s.secret_name} className="flex items-center justify-between gap-2 border-b border-border/40 py-1.5 text-sm">
            <div className="min-w-0">
              <span className="font-mono text-xs">{s.secret_name}</span>
              <p className="text-[10px] text-muted-foreground">
                {s.last_rotated_at ? `${fmtDateTime(s.last_rotated_at)} · ${s.days_since}d / ${s.max_days}d` : "sin rotación registrada"}
              </p>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <Badge variant="outline" className={URGENCY_CLS[s.urgency]}>{URGENCY_LABEL[s.urgency]}</Badge>
              <Button size="sm" variant="outline" onClick={() => setConfirm(s.secret_name)}>Marqué como rotado</Button>
            </div>
          </div>
        ))}
      </CardContent>

      <Dialog open={!!confirm} onOpenChange={(o) => !o && setConfirm(null)}>
        <DialogContent className="max-w-sm">
          <DialogHeader><DialogTitle className="text-sm">Confirmar rotación</DialogTitle></DialogHeader>
          <p className="text-sm text-muted-foreground">
            ¿Registrar que rotaste <span className="font-mono">{confirm}</span> hoy? (no se guarda el valor, solo la fecha)
          </p>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setConfirm(null)}>Cancelar</Button>
            <Button size="sm" disabled={register.isPending}
              onClick={() => { if (confirm) { register.mutate(confirm); setConfirm(null); } }}>
              Confirmar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
