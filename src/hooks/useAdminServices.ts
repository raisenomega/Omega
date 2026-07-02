// Admin CRUD de landing_services (Sitio Web · owner-only). Escritura por Supabase client directo
// (la RLS super_owner de 00085 protege). El admin ve TODOS los servicios (sin filtrar is_visible).
// benefits se limpian de líneas vacías al guardar (el editor los captura uno-por-línea).
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export interface AdminService {
  id: string;
  icon: string;
  title_es: string;
  title_en: string;
  description_es: string;
  description_en: string;
  benefits_es: string[];
  benefits_en: string[];
  display_order: number;
  is_visible: boolean;
}

export type ServiceDraft = Omit<AdminService, "id"> & { id?: string };

const KEY = ["admin_landing_services"];
const COLS =
  "id, icon, title_es, title_en, description_es, description_en, benefits_es, benefits_en, display_order, is_visible";

export function useAdminServices() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: KEY });

  const query = useQuery({
    queryKey: KEY,
    queryFn: async () => {
      const { data, error } = await supabase.from("landing_services").select(COLS).order("display_order");
      if (error) throw error;
      return (data ?? []) as AdminService[];
    },
  });

  const save = useMutation({
    mutationFn: async (s: ServiceDraft) => {
      const payload = {
        icon: s.icon,
        title_es: s.title_es,
        title_en: s.title_en,
        description_es: s.description_es,
        description_en: s.description_en,
        benefits_es: s.benefits_es.map((b) => b.trim()).filter(Boolean),
        benefits_en: s.benefits_en.map((b) => b.trim()).filter(Boolean),
        display_order: s.display_order,
        is_visible: s.is_visible,
      };
      const { error } = s.id
        ? await supabase.from("landing_services").update(payload).eq("id", s.id)
        : await supabase.from("landing_services").insert(payload);
      if (error) throw error;
    },
    onSuccess: invalidate,
  });

  const remove = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("landing_services").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: invalidate,
  });

  const patch = useMutation({
    mutationFn: async ({ id, ...fields }: { id: string } & Partial<Omit<AdminService, "id">>) => {
      const { error } = await supabase.from("landing_services").update(fields).eq("id", id);
      if (error) throw error;
    },
    onSuccess: invalidate,
  });

  return { services: query.data ?? [], isLoading: query.isLoading, save, remove, patch };
}
