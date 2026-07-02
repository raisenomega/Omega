import { useState } from "react";
import { Mail, Phone } from "lucide-react";
import type { Lead } from "@/hooks/useAdminLeads";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const STATUSES = ["new", "contacted", "qualified", "converted", "lost"];

// Una tarjeta de lead: PII (nombre/email/phone/message/audience) + selector de status + notas
// internas. Guardar status y notas van por separado (PATCH status-opcional del backend → editar
// notas no resetea contacted_at). `saving` deshabilita mientras la mutación corre.
export function LeadRow({
  lead,
  onSave,
  saving,
}: {
  lead: Lead;
  onSave: (v: { id: string; status?: string; notes?: string }) => void;
  saving: boolean;
}) {
  const [notes, setNotes] = useState(lead.notes ?? "");

  return (
    <Card>
      <CardContent className="space-y-3 py-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="font-medium text-foreground">
              {lead.name ?? "—"}
              <span className="ml-2 rounded bg-primary/10 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-primary">
                {lead.audience ?? "—"}
              </span>
            </p>
            <p className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-1"><Mail size={12} /> {lead.email}</span>
              {lead.phone && <span className="inline-flex items-center gap-1"><Phone size={12} /> {lead.phone}</span>}
            </p>
          </div>
          <Select value={lead.status} onValueChange={(v) => onSave({ id: lead.id, status: v })} disabled={saving}>
            <SelectTrigger className="h-8 w-36 shrink-0"><SelectValue /></SelectTrigger>
            <SelectContent>
              {STATUSES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>

        {lead.message && <p className="rounded bg-secondary/40 p-2 text-sm text-foreground/80">{lead.message}</p>}

        <div className="flex items-end gap-2">
          <Textarea
            rows={2}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Notas internas…"
            className="text-sm"
          />
          <Button
            size="sm"
            variant="secondary"
            disabled={saving || notes === (lead.notes ?? "")}
            onClick={() => onSave({ id: lead.id, notes })}
          >
            Guardar
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
