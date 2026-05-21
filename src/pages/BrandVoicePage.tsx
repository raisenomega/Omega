import { ComingSoon } from "@/components/ComingSoon";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";

export default function BrandVoicePage() {
  useTrackOnMount("feature_open", { feature: "brand_voice" });
  return (
    <ComingSoon
      title="Brand Voice"
      message="Gestiona la voz y tono de tu marca · En construcción · Próxima funcionalidad."
    />
  );
}
