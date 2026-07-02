import { useState } from "react";
import { useAdminLeads } from "@/hooks/useAdminLeads";
import { LeadRow } from "./LeadRow";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";

const AUDIENCES = [{ v: "", l: "Todos" }, { v: "pyme", l: "PYME" }, { v: "reseller", l: "Agencia" }];
const STATUSES = ["new", "contacted", "qualified", "converted", "lost"];

// Inbox de leads de plataforma (reseller_id NULL) · filtro por audience (pills) + status (select).
// Todo por endpoints guardados del checkpoint A (useAdminLeads). Status select mapea "all"→"" (radix
// no admite value vacío).
export function LeadsInbox() {
  const [audience, setAudience] = useState("");
  const [status, setStatus] = useState("");
  const { leads, isLoading, patch } = useAdminLeads(audience, status);
  const { toast } = useToast();

  const onSave = (v: { id: string; status?: string; notes?: string }) =>
    patch.mutate(v, {
      onError: (e) => toast({ title: "No se pudo guardar", description: e instanceof Error ? e.message : "Error", variant: "destructive" }),
    });

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-1 font-display text-2xl font-bold text-foreground">Leads</h1>
      <p className="mb-6 text-sm text-muted-foreground">Inbox de la landing de plataforma.</p>

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <div className="flex gap-2">
          {AUDIENCES.map((a) => (
            <Button key={a.v} size="sm" variant={audience === a.v ? "default" : "outline"} onClick={() => setAudience(a.v)}>
              {a.l}
            </Button>
          ))}
        </div>
        <Select value={status || "all"} onValueChange={(v) => setStatus(v === "all" ? "" : v)}>
          <SelectTrigger className="h-9 w-40"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Todos los status</SelectItem>
            {STATUSES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <Skeleton className="h-64 w-full" />
      ) : leads.length === 0 ? (
        <p className="text-sm text-muted-foreground">No hay leads todavía.</p>
      ) : (
        <div className="space-y-3">
          {leads.map((l) => <LeadRow key={l.id} lead={l} onSave={onSave} saving={patch.isPending} />)}
        </div>
      )}
    </div>
  );
}
