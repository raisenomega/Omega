import { useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPost, apiPatch } from "@/lib/api-client";

// ARIA · sugerencias proactivas para el cliente (genera idempotente + lista)
export interface ARIASuggestion {
  id: string;
  message: string;
  suggestion_type: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

interface ListResponse {
  suggestions: ARIASuggestion[];
}

const key = (clientId: string) => ["aria", "suggestions", clientId];

export function useAriaSuggestions(clientId: string | null) {
  const enabled = !!clientId;

  // Al montar: POST genera idempotente · best-effort (ignoramos error)
  useEffect(() => {
    if (!clientId) return;
    apiPost<unknown>("/aria/suggestions", { client_id: clientId }).catch(() => {
      /* best-effort · si falla, el GET igual trae lo que haya */
    });
  }, [clientId]);

  const query = useQuery<ARIASuggestion[], Error>({
    queryKey: key(clientId ?? ""),
    queryFn: async () => {
      const res = await apiGet<ListResponse>(`/aria/suggestions?client_id=${clientId}`);
      return res.suggestions;
    },
    enabled,
    staleTime: 30_000,
  });

  const suggestions = query.data ?? [];
  const unread = suggestions.filter((s) => !s.is_read);

  return { suggestions, unread, isLoading: query.isLoading && enabled };
}

export function useMarkSuggestionRead() {
  const qc = useQueryClient();
  return useMutation<{ marked_read: boolean }, Error, string>({
    mutationFn: (id) =>
      apiPatch<{ marked_read: boolean }>(`/aria/suggestions/${id}/read`, {}),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["aria", "suggestions"] });
    },
  });
}
