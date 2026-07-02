// Admin CRUD de landing_process_steps (Sitio Web · owner-only). Escritura por Supabase client directo
// (la RLS super_owner de 00085 protege). El admin ve TODOS los pasos (sin filtrar is_visible).
// Espejo de useAdminServices, sin benefits y con step_number.
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export interface AdminProcessStep {
  id: string;
  step_number: number;
  icon: string;
  title_es: string;
  title_en: string;
  description_es: string;
  description_en: string;
  display_order: number;
  is_visible: boolean;
}

export type ProcessDraft = Omit<AdminProcessStep, "id"> & { id?: string };

const KEY = ["admin_landing_process"];
const COLS = "id, step_number, icon, title_es, title_en, description_es, description_en, display_order, is_visible";

export function useAdminProcess() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: KEY });

  const query = useQuery({
    queryKey: KEY,
    queryFn: async () => {
      const { data, error } = await supabase.from("landing_process_steps").select(COLS).order("display_order");
      if (error) throw error;
      return (data ?? []) as AdminProcessStep[];
    },
  });

  const save = useMutation({
    mutationFn: async (s: ProcessDraft) => {
      const payload = {
        step_number: s.step_number,
        icon: s.icon,
        title_es: s.title_es,
        title_en: s.title_en,
        description_es: s.description_es,
        description_en: s.description_en,
        display_order: s.display_order,
        is_visible: s.is_visible,
      };
      const { error } = s.id
        ? await supabase.from("landing_process_steps").update(payload).eq("id", s.id)
        : await supabase.from("landing_process_steps").insert(payload);
      if (error) throw error;
    },
    onSuccess: invalidate,
  });

  const remove = useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("landing_process_steps").delete().eq("id", id);
      if (error) throw error;
    },
    onSuccess: invalidate,
  });

  const patch = useMutation({
    mutationFn: async ({ id, ...fields }: { id: string } & Partial<Omit<AdminProcessStep, "id">>) => {
      const { error } = await supabase.from("landing_process_steps").update(fields).eq("id", id);
      if (error) throw error;
    },
    onSuccess: invalidate,
  });

  return { steps: query.data ?? [], isLoading: query.isLoading, save, remove, patch };
}
