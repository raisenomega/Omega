import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

// Signed URL del logo existente (bucket brand-files es PRIVADO · la URL pública /object/public/
// devuelve 404). Usado por el wizard SectionBrandAssets para mostrar thumbnail al re-editar.
export function useExistingBrandLogoUrl(logoFileId: string | null | undefined, enabled = true) {
  return useQuery({
    queryKey: ["wizard_logo_signed", logoFileId],
    queryFn: async () => {
      const f = await supabase.from("brand_files").select("storage_path").eq("id", logoFileId!).maybeSingle();
      if (!f.data?.storage_path) return null;
      const s = await supabase.storage.from("brand-files").createSignedUrl(f.data.storage_path, 3600);
      return s.data?.signedUrl ?? null;
    },
    enabled: !!logoFileId && enabled,
  });
}
