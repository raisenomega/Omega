// Inbox de leads de plataforma (Sitio Web · owner-only). SIEMPRE vía endpoints backend guardados:
// GET /platform/leads (super_owner) + PATCH /resellers/leads/{id}/status (status y/o notes) — NUNCA
// Supabase directo (regla del arco · leads solo por endpoints con guard). Filtra audience + status.
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPatch } from "@/lib/api-client";

export interface Lead {
  id: string;
  name: string | null;
  email: string;
  phone: string | null;
  message: string | null;
  audience: string | null;
  status: string;
  notes: string | null;
  created_at: string;
}

interface LeadsResponse {
  data: { leads: Lead[]; total: number };
}

const KEY = "platform_leads";

export function useAdminLeads(audience: string, status: string) {
  const qc = useQueryClient();

  const query = useQuery({
    queryKey: [KEY, audience, status],
    queryFn: async () => {
      const p = new URLSearchParams();
      if (audience) p.set("audience", audience);
      if (status) p.set("status", status);
      const qs = p.toString();
      const res = await apiGet<LeadsResponse>(`/platform/leads${qs ? `?${qs}` : ""}`);
      return res.data.leads;
    },
  });

  const patch = useMutation({
    mutationFn: (v: { id: string; status?: string; notes?: string }) =>
      apiPatch(`/resellers/leads/${v.id}/status`, { status: v.status, notes: v.notes }),
    onSuccess: () => qc.invalidateQueries({ queryKey: [KEY] }),
  });

  return { leads: query.data ?? [], isLoading: query.isLoading, patch };
}
