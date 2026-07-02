import { useMemo, useState } from "react";
import { useAdminLeads, type Lead } from "@/hooks/useAdminLeads";
import { LeadsFilters, type FilterState } from "./leads/LeadsFilters";
import { LeadsStats } from "./leads/LeadsStats";
import { LeadsTable } from "./leads/LeadsTable";
import { LeadViewDialog } from "./leads/LeadViewDialog";
import { LeadEditDialog } from "./leads/LeadEditDialog";
import { LeadNotesDialog } from "./leads/LeadNotesDialog";
import { LeadEmailDialog } from "./leads/LeadEmailDialog";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";

// CRM — Leads · réplica del AdminLeads del molde + extensiones (D5/D6/D7) + email/notify. Full-width
// (pieza 1: sin max-width · el p-6 de AppLayout da el borde). Todo por endpoints guardados (hook).
const EMPTY: FilterState = { search: "", status: "", temp: "", audience: "", source: "" };

export function LeadsInbox() {
  const { leads, isLoading, update, remove, email, notify } = useAdminLeads();
  const { toast } = useToast();
  const [filters, setFilters] = useState<FilterState>(EMPTY);
  const [viewing, setViewing] = useState<Lead | null>(null);
  const [editing, setEditing] = useState<Lead | null>(null);
  const [noting, setNoting] = useState<Lead | null>(null);
  const [emailing, setEmailing] = useState<Lead | null>(null);

  const onErr = (e: unknown) =>
    toast({ title: "No se pudo guardar", description: e instanceof Error ? e.message : "Error", variant: "destructive" });
  const save = (v: { id: string } & Partial<Omit<Lead, "id">>, close?: () => void) =>
    update.mutate(v, { onError: onErr, onSuccess: close });

  const onSend = (id: string, subject: string, message: string) =>
    email.mutate({ id, subject, message }, { onSuccess: () => { setEmailing(null); toast({ title: "Email enviado" }); } });
  const emailError = !email.isError
    ? null
    : /not_configured/.test(String(email.error)) ? "Email no configurado en el servidor (falta RESEND_API_KEY)."
    : /resend_rejected/.test(String(email.error)) ? "Resend rechazó el envío. Configura un dominio verificado en Resend."
    : email.error instanceof Error ? email.error.message : "No se pudo enviar.";

  const onNotify = (lead: Lead) =>
    notify.mutate(lead.id, {
      onError: onErr,
      onSuccess: (res) =>
        res?.data?.notified
          ? toast({ title: `Notificado a ${lead.email}` })
          : toast({ title: "Aún no es usuario", description: "Este lead todavía no tiene cuenta en OMEGA." }),
    });

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
    <div>
      <h1 className="mb-6 font-display text-2xl font-bold text-foreground">CRM — Leads</h1>
      <LeadsFilters value={filters} set={(p) => setFilters((f) => ({ ...f, ...p }))} sources={sources} />
      <LeadsStats leads={leads} />
      <LeadsTable
        leads={filtered}
        onView={setViewing}
        onEmail={setEmailing}
        onNotify={onNotify}
        onNotes={setNoting}
        onEdit={setEditing}
        onStatus={(id, status) => save({ id, status })}
        onTemp={(id, temperature) => save({ id, temperature })}
        onDelete={(id) => remove.mutate(id, { onError: onErr })}
      />
      <LeadViewDialog lead={viewing} onClose={() => setViewing(null)} />
      <LeadEditDialog lead={editing} onClose={() => setEditing(null)} onSave={(id, fields) => save({ id, ...fields }, () => setEditing(null))} />
      <LeadNotesDialog lead={noting} onClose={() => setNoting(null)} onSave={(id, notes) => save({ id, notes }, () => setNoting(null))} />
      <LeadEmailDialog lead={emailing} onClose={() => setEmailing(null)} onSend={onSend} sending={email.isPending} error={emailError} />
    </div>
  );
}
