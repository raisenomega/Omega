import { ComingSoon } from "@/components/ComingSoon";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";

export default function CrisisPage() {
  useTrackOnMount("feature_open", { feature: "crisis_room" });
  return (
    <ComingSoon
      title="Crisis Room · Add-on $25/mes"
      message="Monitoreo y gestión de crisis · Disponible próximamente."
    />
  );
}
