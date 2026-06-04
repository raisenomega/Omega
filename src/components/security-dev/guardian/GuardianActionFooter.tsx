import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Loader2, ShieldX, Wrench, Bot } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { resolveIncident } from "@/lib/guardian/actions";
import { GuardianActionPanel } from "./GuardianActionPanel";
import { GuardianClaudeConsultPanel } from "./GuardianClaudeConsultPanel";
import type { GuardianUserDetail, OpenGuardianDetail } from "@/types/guardian";

// Footer del modal (Sub-B) · 3 botones tipo SENTINEL. [Consultar Claude] = preview hasta Sub-E.
export function GuardianActionFooter({ detail, userDetail, onClose }: { detail: OpenGuardianDetail; userDetail?: GuardianUserDetail; onClose: () => void }) {
  const { toast } = useToast();
  const qc = useQueryClient();
  const [showActions, setShowActions] = useState(false);
  const [showConsult, setShowConsult] = useState(false);
  const [fpBusy, setFpBusy] = useState(false);

  const markFalsePositive = async () => {
    if (!detail.incidentId) return;
    setFpBusy(true);
    try {
      await resolveIncident({ incident_id: detail.incidentId, resolution_notes: "Marcado falso positivo por el owner", false_positive: true });
      toast({ title: "Marcado como falso positivo" });
      ["guardian-incidents", "guardian-user-detail"].forEach((k) => qc.invalidateQueries({ queryKey: [k] }));
      onClose();
    } catch (e) {
      toast({ variant: "destructive", title: "No se pudo marcar", description: e instanceof Error ? e.message : "Error" });
    } finally { setFpBusy(false); }
  };

  return (
    <div className="space-y-2 border-t border-border/40 pt-2">
      <div className="flex flex-wrap gap-2">
        {detail.incidentId && (
          <Button size="sm" variant="outline" disabled={fpBusy} onClick={markFalsePositive}>
            {fpBusy ? <Loader2 className="h-3 w-3 animate-spin" /> : <ShieldX className="h-3 w-3" />}<span className="ml-1">Falso positivo</span>
          </Button>
        )}
        <Button size="sm" variant={showActions ? "default" : "outline"} onClick={() => setShowActions((v) => !v)}>
          <Wrench className="h-3 w-3" /><span className="ml-1">Tomar acción</span>
        </Button>
        <Button size="sm" variant={showConsult ? "default" : "ghost"} onClick={() => setShowConsult((v) => !v)}>
          <Bot className="h-3 w-3" /><span className="ml-1">Consultar con Claude</span>
        </Button>
      </div>
      {showActions && <GuardianActionPanel detail={detail} userDetail={userDetail} onDone={onClose} />}
      {showConsult && <GuardianClaudeConsultPanel detail={detail} />}
    </div>
  );
}
