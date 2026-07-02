// Pasos del proceso de la landing (lectura pública · RLS SELECT true). Filtra is_visible (col 00087)
// y ordena por display_order. Bilingüe: columnas _es/_en crudas · el componente elige el idioma.
// CRUD del owner vive en el editor (Checkpoint C).
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export interface LandingProcessStep {
  id: string;
  step_number: number;
  icon: string;
  title_es: string;
  title_en: string;
  description_es: string;
  description_en: string;
  display_order: number;
}

export function useLandingProcess() {
  const { data, isLoading } = useQuery({
    queryKey: ["landing_process_steps"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("landing_process_steps")
        .select("id, step_number, icon, title_es, title_en, description_es, description_en, display_order")
        .eq("is_visible", true)
        .order("display_order");
      if (error) throw error;
      return (data ?? []) as LandingProcessStep[];
    },
  });
  return { steps: data ?? [], isLoading };
}
