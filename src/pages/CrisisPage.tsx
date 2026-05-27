import { ComingSoon } from "@/components/ComingSoon";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { useProAccess } from "@/hooks/useProAccess";
import { ProFeatureGate, ProGateLoading } from "@/components/ProFeatureGate";

export default function CrisisPage() {
  useTrackOnMount("feature_open", { feature: "crisis_room" });
  const access = useProAccess();
  if (access.loading) return <ProGateLoading />;
  if (!access.hasPro)
    return <ProFeatureGate feature="Crisis Room" description="Monitoreo y gestión de crisis de marca." clientId={access.clientId} />;
  return (
    <ComingSoon
      title="Crisis Room · Add-on $25/mes"
      message="Monitoreo y gestión de crisis · Disponible próximamente."
    />
  );
}
