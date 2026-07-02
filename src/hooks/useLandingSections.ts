import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

// Fase 3 · lee landing_sections (RLS lectura pública → anon OK · la landing es pública).
// Adaptado a OMEGA: la tabla solo tiene name/is_visible/display_order (el copy vive en i18n,
// decisión owner) → expone isVisible + orden, SIN getText. Default optimista true (no esconde
// el hero durante la carga · el hero debe renderizar sin esperar · base del prerender de F4).
export interface LandingSection {
  id: string;
  name: string;
  is_visible: boolean;
  display_order: number;
}

export function useLandingSections() {
  const { data } = useQuery({
    queryKey: ["landing_sections"],
    queryFn: async (): Promise<LandingSection[]> => {
      const { data, error } = await supabase
        .from("landing_sections")
        .select("*")
        .order("display_order");
      if (error) throw error;
      return (data ?? []) as unknown as LandingSection[];
    },
  });

  const sections = data ?? [];
  const isVisible = (name: string): boolean => {
    const s = sections.find((x) => x.name === name);
    return s ? s.is_visible : true; // ausente/cargando → visible (optimista)
  };

  return { sections, isVisible };
}
