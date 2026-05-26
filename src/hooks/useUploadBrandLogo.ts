import { useMutation, useQueryClient } from "@tanstack/react-query";
import { uploadBrandFile, patchOnboarding } from "@/lib/onboarding-api";
import type { OnboardingForm } from "@/lib/onboarding-schema";

interface Input { clientId: string; files: File[]; data: OnboardingForm; }

// DEBT-059: persiste los archivos del wizard (SectionBrandAssets · antes se descartaban
// porque los File[] no serializan a JSON y nadie los subía). El primer image/* →
// file_category 'logo' → enlaza client_brand_assets.logo_file_id (lo consume el overlay
// del Content Lab vía find_client_logo_url); el resto → 'other' (guardados para uso futuro).
// Best-effort por archivo: un fallo de subida no bloquea la creación/edición del cliente.
export function useUploadBrandLogo() {
  const qc = useQueryClient();
  return useMutation<void, Error, Input>({
    mutationFn: async ({ clientId, files, data }) => {
      let logoId: string | null = data.brand_assets?.logo_file_id ?? null;
      let logoTaken = false;
      for (const file of files) {
        const isLogo = !logoTaken && file.type.startsWith("image/");
        try {
          const r = await uploadBrandFile(clientId, file, isLogo ? "logo" : "other");
          if (isLogo) { logoId = r.id; logoTaken = true; }
        } catch (e) {
          console.warn("[brand-logo] subida falló para", file.name, e);
        }
      }
      if (logoId) {
        const assets = { ...(data.brand_assets ?? {}), logo_file_id: logoId, logo_files: undefined } as OnboardingForm["brand_assets"];
        await patchOnboarding(clientId, { ...data, brand_assets: assets });
      }
    },
    onSuccess: (_v, { clientId }) => {
      qc.invalidateQueries({ queryKey: ["client_onboarding_data", clientId] });
    },
  });
}
