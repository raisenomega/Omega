import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import type { Lead } from "@/hooks/useAdminLeads";

interface Props {
  lead: Lead | null;
  onClose: () => void;
  onSend: (id: string, subject: string, message: string) => void;
  sending: boolean;
  error: string | null; // error honesto de Resend (dominio no verificado / no configurado)
}

// Diálogo ✈ email al lead (D-C · asunto≤200 / mensaje≤5000 · texto plano). El error de Resend se
// muestra VISIBLE (rojo) · nunca "Enviado" falso. Al éxito el padre cierra.
export function LeadEmailDialog({ lead, onClose, onSend, sending, error }: Props) {
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  useEffect(() => { setSubject(""); setMessage(""); }, [lead]);

  return (
    <Dialog open={!!lead} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader><DialogTitle>Email a {lead?.name ?? lead?.email}</DialogTitle></DialogHeader>
        {lead && (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">Se enviará a: <strong>{lead.email}</strong></p>
            <div><Label>Asunto</Label><Input value={subject} onChange={(e) => setSubject(e.target.value)} maxLength={200} /></div>
            <div><Label>Mensaje</Label><Textarea rows={6} value={message} onChange={(e) => setMessage(e.target.value)} maxLength={5000} /></div>
            {error && <p className="rounded bg-destructive/10 p-2 text-sm text-destructive">{error}</p>}
            <Button className="w-full" disabled={sending || !subject.trim() || !message.trim()} onClick={() => onSend(lead.id, subject, message)}>
              {sending ? "Enviando…" : "Enviar email"}
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
