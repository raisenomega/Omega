// Notificaciones in-app del usuario actual (dashboard) · por endpoints guardados (GET /notifications
// + PATCH /{id}/read) · el token de la sesión va en apiGet/apiPatch. Cero Supabase directo.
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPatch } from "@/lib/api-client";

export interface Notification {
  id: string;
  type: string;
  title: string;
  body: string | null;
  is_read: boolean;
  created_at: string;
}

interface Resp {
  data: { notifications: Notification[]; unread: number };
}

const KEY = ["notifications"];

export function useNotifications() {
  const qc = useQueryClient();
  const query = useQuery({
    queryKey: KEY,
    queryFn: async () => (await apiGet<Resp>("/notifications")).data,
  });
  const markRead = useMutation({
    mutationFn: (id: string) => apiPatch(`/notifications/${id}/read`, {}),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  });
  return { notifications: query.data?.notifications ?? [], unread: query.data?.unread ?? 0, markRead };
}
