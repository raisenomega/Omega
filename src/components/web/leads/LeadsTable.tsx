import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { LeadTableRow } from "./LeadTableRow";
import type { Lead } from "@/hooks/useAdminLeads";

const COLS = ["Nombre", "Email", "Audiencia", "Fuente", "Estado", "Temperatura", "Fecha"];

interface Props {
  leads: Lead[];
  onView: (l: Lead) => void;
  onEmail: (l: Lead) => void;
  onNotify: (l: Lead) => void;
  onNotes: (l: Lead) => void;
  onEdit: (l: Lead) => void;
  onStatus: (id: string, v: string) => void;
  onTemp: (id: string, v: string) => void;
  onDelete: (id: string) => void;
}

export function LeadsTable({ leads, ...cb }: Props) {
  return (
    <div className="overflow-auto rounded-lg border border-border bg-card">
      <Table>
        <TableHeader>
          <TableRow>
            {COLS.map((c) => <TableHead key={c}>{c}</TableHead>)}
            <TableHead className="text-right">Acciones</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {leads.map((l) => <LeadTableRow key={l.id} lead={l} {...cb} />)}
          {leads.length === 0 && (
            <TableRow>
              <TableCell colSpan={8} className="py-12 text-center text-muted-foreground">
                No hay leads registrados.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
