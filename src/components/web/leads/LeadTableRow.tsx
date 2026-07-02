import { format } from "date-fns";
import { Eye, StickyNote, Pencil, MessageCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TableCell, TableRow } from "@/components/ui/table";
import { ConfirmDeleteButton } from "@/components/web/ConfirmDeleteButton";
import { InlineBadgeSelect } from "./InlineBadgeSelect";
import type { Lead } from "@/hooks/useAdminLeads";
import {
  STATUSES, STATUS_LABELS, STATUS_COLORS, TEMPERATURES, TEMP_LABELS, TEMP_COLORS, AUDIENCE_LABELS, waLink,
} from "./lead-constants";

interface Props {
  lead: Lead;
  onView: (l: Lead) => void;
  onNotes: (l: Lead) => void;
  onEdit: (l: Lead) => void;
  onStatus: (id: string, v: string) => void;
  onTemp: (id: string, v: string) => void;
  onDelete: (id: string) => void;
}

// Una fila del CRM · réplica del molde + extensiones (Audiencia D5, Fuente D7, WhatsApp D6).
export function LeadTableRow({ lead, onView, onNotes, onEdit, onStatus, onTemp, onDelete }: Props) {
  const wa = waLink(lead);
  return (
    <TableRow>
      <TableCell className="font-medium">{lead.name ?? "—"}</TableCell>
      <TableCell className="text-sm text-muted-foreground">{lead.email}</TableCell>
      <TableCell><Badge variant="outline" className="text-xs">{AUDIENCE_LABELS[lead.audience ?? ""] ?? "—"}</Badge></TableCell>
      <TableCell className="text-xs text-muted-foreground">{lead.source ?? "—"}</TableCell>
      <TableCell>
        <InlineBadgeSelect value={lead.status} options={STATUSES} labels={STATUS_LABELS} colors={STATUS_COLORS} onChange={(v) => onStatus(lead.id, v)} />
      </TableCell>
      <TableCell>
        <InlineBadgeSelect value={lead.temperature} options={TEMPERATURES} labels={TEMP_LABELS} colors={TEMP_COLORS} onChange={(v) => onTemp(lead.id, v)} />
      </TableCell>
      <TableCell className="text-xs text-muted-foreground">{format(new Date(lead.created_at), "dd/MM/yy")}</TableCell>
      <TableCell>
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onView(lead)} title="Ver detalle"><Eye size={14} /></Button>
          {wa ? (
            <a href={wa} target="_blank" rel="noopener noreferrer" title="WhatsApp">
              <Button variant="ghost" size="icon" className="h-7 w-7 text-green-500"><MessageCircle size={14} /></Button>
            </a>
          ) : (
            <Button variant="ghost" size="icon" className="h-7 w-7 opacity-40" disabled title="Sin teléfono ni usuario"><MessageCircle size={14} /></Button>
          )}
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onNotes(lead)} title="Notas"><StickyNote size={14} /></Button>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onEdit(lead)} title="Editar"><Pencil size={14} /></Button>
          <ConfirmDeleteButton label={lead.name ?? lead.email} onConfirm={() => onDelete(lead.id)} />
        </div>
      </TableCell>
    </TableRow>
  );
}
