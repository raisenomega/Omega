// Inbox de leads de plataforma (Sitio Web · super_owner). SIEMPRE por endpoints backend guardados
// (GET /platform/leads + PATCH /resellers/leads/{id}/status + DELETE) · NUNCA Supabase directo
// (el AdminLeads del molde escribía directo → NO se replica). Carga todo (limit 100) y filtra en
// cliente como el molde (useMemo). update acepta cualquier campo editable; remove borra.
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPatch, apiDelete } from "@/lib/api-client";

export interface Lead {
  id: string;
  name: string | null;
  email: string;
  phone: string | null;
  message: string | null;
  audience: string | null;
  status: string;
  temperature: string | null;
  notes: string | null;
  company: string | null;
  whatsapp_username: string | null;
  source: string | null;
  created_at: string;
}

interface LeadsResponse {
  data: { leads: Lead[] };
}

const KEY = ["platform_leads"];

export function useAdminLeads() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: KEY });

  const query = useQuery({
    queryKey: KEY,
    queryFn: async () => {
      const res = await apiGet<LeadsResponse>("/platform/leads?limit=100");
      return res.data.leads;
    },
  });

  const update = useMutation({
    mutationFn: (v: { id: string } & Partial<Omit<Lead, "id">>) => {
      const { id, ...fields } = v;
      return apiPatch(`/resellers/leads/${id}/status`, fields);
    },
    onSuccess: invalidate,
  });

  const remove = useMutation({
    mutationFn: (id: string) => apiDelete(`/resellers/leads/${id}`),
    onSuccess: invalidate,
  });

  return { leads: query.data ?? [], isLoading: query.isLoading, update, remove };
}
