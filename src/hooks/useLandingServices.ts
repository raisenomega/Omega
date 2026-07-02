// Servicios de la landing (lectura pública · RLS SELECT true). Filtra is_visible (col 00086) y
// ordena por display_order. Bilingüe: expone las columnas _es/_en crudas · el componente elige
// el idioma con LandingLangContext. Escritura/CRUD del owner vive en el editor (Checkpoint C).
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export interface LandingService {
  id: string;
  icon: string;
  title_es: string;
  title_en: string;
  description_es: string;
  description_en: string;
  benefits_es: string[];
  benefits_en: string[];
  display_order: number;
}

export function useLandingServices() {
  const { data, isLoading } = useQuery({
    queryKey: ["landing_services"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("landing_services")
        .select("id, icon, title_es, title_en, description_es, description_en, benefits_es, benefits_en, display_order")
        .eq("is_visible", true)
        .order("display_order");
      if (error) throw error;
      return (data ?? []) as LandingService[];
    },
  });
  return { services: data ?? [], isLoading };
}
