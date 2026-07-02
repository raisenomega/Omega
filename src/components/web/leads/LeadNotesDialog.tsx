import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import type { Lead } from "@/hooks/useAdminLeads";

interface Props {
  lead: Lead | null;
  onClose: () => void;
  onSave: (id: string, notes: string) => void;
}

// Notas internas (réplica del Notes dialog del molde). Guarda vía PATCH guardado (notes='' limpia).
export function LeadNotesDialog({ lead, onClose, onSave }: Props) {
  const [notes, setNotes] = useState("");
  useEffect(() => setNotes(lead?.notes ?? ""), [lead]);

  return (
    <Dialog open={!!lead} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader><DialogTitle>Notas — {lead?.name ?? lead?.email}</DialogTitle></DialogHeader>
        <Textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={6} placeholder="Escribe tus notas aquí..." />
        {lead && <Button className="w-full" onClick={() => onSave(lead.id, notes)}>Guardar nota</Button>}
      </DialogContent>
    </Dialog>
  );
}
