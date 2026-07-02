import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import type { Lead } from "@/hooks/useAdminLeads";

type Editable = Pick<Lead, "name" | "email" | "phone" | "company" | "whatsapp_username" | "message">;

interface Props {
  lead: Lead | null;
  onClose: () => void;
  onSave: (id: string, fields: Partial<Editable>) => void;
}

// Editar campos del lead (réplica del Edit dialog del molde · +company/whatsapp). Guarda vía PATCH
// guardado (nunca Supabase directo). Se resetea cuando cambia el lead.
export function LeadEditDialog({ lead, onClose, onSave }: Props) {
  const [f, setF] = useState<Editable>({ name: "", email: "", phone: "", company: "", whatsapp_username: "", message: "" });
  useEffect(() => {
    if (lead) setF({ name: lead.name ?? "", email: lead.email, phone: lead.phone ?? "", company: lead.company ?? "", whatsapp_username: lead.whatsapp_username ?? "", message: lead.message ?? "" });
  }, [lead]);
  const set = (p: Partial<Editable>) => setF((prev) => ({ ...prev, ...p }));

  return (
    <Dialog open={!!lead} onOpenChange={onClose}>
      <DialogContent className="max-h-[80vh] overflow-auto">
        <DialogHeader><DialogTitle>Editar Lead</DialogTitle></DialogHeader>
        {lead && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div><Label>Nombre</Label><Input value={f.name ?? ""} onChange={(e) => set({ name: e.target.value })} /></div>
              <div><Label>Email</Label><Input value={f.email ?? ""} onChange={(e) => set({ email: e.target.value })} /></div>
              <div><Label>Teléfono</Label><Input value={f.phone ?? ""} onChange={(e) => set({ phone: e.target.value })} /></div>
              <div><Label>Empresa</Label><Input value={f.company ?? ""} onChange={(e) => set({ company: e.target.value })} /></div>
              <div><Label>WhatsApp (usuario)</Label><Input value={f.whatsapp_username ?? ""} onChange={(e) => set({ whatsapp_username: e.target.value })} /></div>
            </div>
            <div><Label>Mensaje</Label><Textarea value={f.message ?? ""} onChange={(e) => set({ message: e.target.value })} /></div>
            <Button className="w-full" onClick={() => onSave(lead.id, f)}>Guardar</Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
