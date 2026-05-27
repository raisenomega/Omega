import { useState } from "react";
import { AlertTriangle, X } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { getPlanConfig, type PlanCode } from "@/lib/plan-limits";
import { computeLostItems } from "./_compute_lost_items";
import { useScheduleDowngrade } from "@/hooks/useScheduleDowngrade";
import { useClientAddonFeatureKeys } from "@/hooks/useClientAddonFeatureKeys";

interface PlanDowngradeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  targetPlan: PlanCode;
  currentPlan: PlanCode;
  renewsOn: string | null;
  clientId: string;
}

export function PlanDowngradeDialog({ open, onOpenChange, targetPlan, currentPlan, renewsOn, clientId }: PlanDowngradeDialogProps) {
  const [accepted, setAccepted] = useState(false);
  const schedule = useScheduleDowngrade(() => { setAccepted(false); onOpenChange(false); });
  const ownedFeatureKeys = useClientAddonFeatureKeys(clientId);
  const targetLabel = getPlanConfig(targetPlan).label;
  const parsed = renewsOn ? new Date(renewsOn) : null;
  const effectiveDate = parsed && !isNaN(parsed.getTime())
    ? parsed.toLocaleDateString("es-AR", { day: "2-digit", month: "long", year: "numeric" })
    : null;
  const effectivePhrase = effectiveDate ? `el ${effectiveDate}` : "al final de tu ciclo actual";
  const lostItems = computeLostItems(currentPlan, targetPlan, ownedFeatureKeys);
  const lostSummary = lostItems.length > 0 ? lostItems.join(", ") : "las funciones listadas";
  const consentLabel = `Entiendo que mi plan cambiará a ${targetLabel} ${effectivePhrase} y perderé acceso a ${lostSummary}`;

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) setAccepted(false); onOpenChange(o); }}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Bajar a {targetLabel}</DialogTitle>
        </DialogHeader>

        <p className="text-sm text-muted-foreground">
          El cambio se aplicará <span className="font-medium text-foreground">{effectivePhrase}</span>.
        </p>

        <div className="rounded-md border border-amber-500/30 bg-amber-500/5 p-3">
          {lostItems.length > 0 ? (
            <ul className="space-y-1.5">
              {lostItems.map((item) => (
                <li key={item} className="flex gap-2 text-xs text-muted-foreground">
                  <X className="h-3.5 w-3.5 shrink-0 mt-0.5 text-destructive" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="flex gap-2 text-xs text-muted-foreground">
              <AlertTriangle className="h-3.5 w-3.5 shrink-0 mt-0.5 text-amber-500" />
              <span>Sin pérdida de funciones · solo cambia el volumen</span>
            </p>
          )}
        </div>

        <label className="flex items-start gap-2 text-xs text-muted-foreground cursor-pointer">
          <Checkbox
            checked={accepted}
            onCheckedChange={(c) => setAccepted(c === true)}
            className="mt-0.5"
          />
          <span>{consentLabel}</span>
        </label>

        <DialogFooter>
          <Button variant="secondary" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button
            className="w-full"
            disabled={!accepted || schedule.isPending}
            onClick={() => schedule.mutate({ clientId, targetPlan: targetPlan as "basic" | "pro" })}
          >
            {schedule.isPending ? "Programando…" : "Confirmar cambio"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
