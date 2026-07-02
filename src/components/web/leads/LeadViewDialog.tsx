import { format } from "date-fns";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import type { Lead } from "@/hooks/useAdminLeads";
import { AUDIENCE_LABELS, STATUS_LABELS, TEMP_LABELS } from "./lead-constants";

// Detalle read-only del lead (réplica del View dialog del molde · adaptado a campos OMEGA).
export function LeadViewDialog({ lead, onClose }: { lead: Lead | null; onClose: () => void }) {
  const F = ({ k, v }: { k: string; v: string }) => (
    <div><span className="text-muted-foreground">{k}:</span> {v || "—"}</div>
  );
  return (
    <Dialog open={!!lead} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader><DialogTitle>Detalle del Lead</DialogTitle></DialogHeader>
        {lead && (
          <div className="space-y-3 text-sm">
            <div className="grid grid-cols-2 gap-3">
              <F k="Nombre" v={lead.name ?? ""} />
              <F k="Email" v={lead.email} />
              <F k="Teléfono" v={lead.phone ?? ""} />
              <F k="Empresa" v={lead.company ?? ""} />
              <F k="WhatsApp" v={lead.whatsapp_username ?? ""} />
              <F k="Audiencia" v={AUDIENCE_LABELS[lead.audience ?? ""] ?? "—"} />
              <F k="Fuente" v={lead.source ?? ""} />
              <F k="Estado" v={STATUS_LABELS[lead.status] ?? lead.status} />
              <F k="Temperatura" v={TEMP_LABELS[lead.temperature ?? ""] ?? "—"} />
              <F k="Fecha" v={format(new Date(lead.created_at), "dd/MM/yyyy HH:mm")} />
            </div>
            <div>
              <span className="text-muted-foreground">Mensaje:</span>
              <p className="mt-1 whitespace-pre-wrap rounded bg-secondary/50 p-3">{lead.message || "—"}</p>
            </div>
            {lead.notes && (
              <div>
                <span className="text-muted-foreground">Notas:</span>
                <p className="mt-1 whitespace-pre-wrap rounded bg-secondary/50 p-3">{lead.notes}</p>
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
