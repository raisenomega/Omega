import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useLandingLang } from "@/landing/i18n/LandingLangContext";

// Footer mínimo de la landing (Rebanada 1): marca OMEGA + rights de landing_footer_config
// ("Una plataforma de Raisen Agency"). RLS lectura pública → anon OK. Fallback a i18n si aún vacío.
export function LandingFooter() {
  const { lang, t } = useLandingLang();
  const { data } = useQuery({
    queryKey: ["landing_footer_config"],
    queryFn: async () => {
      const { data } = await supabase
        .from("landing_footer_config")
        .select("rights_es, rights_en")
        .limit(1)
        .maybeSingle();
      return data as { rights_es: string; rights_en: string } | null;
    },
  });
  const rights = data ? (lang === "es" ? data.rights_es : data.rights_en) : t.footer.rights;

  return (
    <footer className="relative z-10 border-t border-white/10 bg-background/60 px-6 py-8 text-center">
      <span className="font-display text-base font-bold text-white">
        OMEGA<span className="text-[#EEA62B]">.</span>
      </span>
      <p className="mt-2 text-xs text-white/50">{rights}</p>
    </footer>
  );
}
