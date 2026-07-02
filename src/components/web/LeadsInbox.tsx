import { useMemo, useState } from "react";
import { useAdminLeads, type Lead } from "@/hooks/useAdminLeads";
import { LeadsFilters, type FilterState } from "./leads/LeadsFilters";
import { LeadsStats } from "./leads/LeadsStats";
import { LeadsTable } from "./leads/LeadsTable";
import { LeadViewDialog } from "./leads/LeadViewDialog";
import { LeadEditDialog } from "./leads/LeadEditDialog";
import { LeadNotesDialog } from "./leads/LeadNotesDialog";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";

// CRM — Leads · réplica 1:1 del AdminLeads del molde (título, buscador, 4 stats, tabla con badges +
// selects inline, acciones ver/notas/editar/eliminar/WhatsApp) + extensiones D5/D6/D7. Filtrado en
// cliente (useMemo, como el molde) sobre lo cargado. Toda escritura por endpoints guardados (hook).
const EMPTY: FilterState = { search: "", status: "", temp: "", audience: "", source: "" };

export function LeadsInbox() {
  const { leads, isLoading, update, remove } = useAdminLeads();
  const { toast } = useToast();
  const [filters, setFilters] = useState<FilterState>(EMPTY);
  const [viewing, setViewing] = useState<Lead | null>(null);
  const [editing, setEditing] = useState<Lead | null>(null);
  const [noting, setNoting] = useState<Lead | null>(null);

  const onErr = (e: unknown) =>
    toast({ title: "No se pudo guardar", description: e instanceof Error ? e.message : "Error", variant: "destructive" });
  const save = (v: { id: string } & Partial<Omit<Lead, "id">>, close?: () => void) =>
    update.mutate(v, { onError: onErr, onSuccess: close });

  const sources = useMemo(() => [...new Set(leads.map((l) => l.source).filter(Boolean) as string[])], [leads]);
  const filtered = useMemo(
    () =>
      leads.filter((l) => {
        if (filters.status && l.status !== filters.status) return false;
        if (filters.temp && l.temperature !== filters.temp) return false;
        if (filters.audience && l.audience !== filters.audience) return false;
        if (filters.source && l.source !== filters.source) return false;
        if (filters.search) {
          const q = filters.search.toLowerCase();
          return (l.name ?? "").toLowerCase().includes(q) || l.email.toLowerCase().includes(q) || (l.company ?? "").toLowerCase().includes(q);
        }
        return true;
      }),
    [leads, filters],
  );

  if (isLoading) return <Skeleton className="h-96 w-full" />;

  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="mb-6 font-display text-2xl font-bold text-foreground">CRM — Leads</h1>
      <LeadsFilters value={filters} set={(p) => setFilters((f) => ({ ...f, ...p }))} sources={sources} />
      <LeadsStats leads={leads} />
      <LeadsTable
        leads={filtered}
        onView={setViewing}
        onNotes={setNoting}
        onEdit={setEditing}
        onStatus={(id, status) => save({ id, status })}
        onTemp={(id, temperature) => save({ id, temperature })}
        onDelete={(id) => remove.mutate(id, { onError: onErr })}
      />
      <LeadViewDialog lead={viewing} onClose={() => setViewing(null)} />
      <LeadEditDialog lead={editing} onClose={() => setEditing(null)} onSave={(id, fields) => save({ id, ...fields }, () => setEditing(null))} />
      <LeadNotesDialog lead={noting} onClose={() => setNoting(null)} onSave={(id, notes) => save({ id, notes }, () => setNoting(null))} />
    </div>
  );
}
