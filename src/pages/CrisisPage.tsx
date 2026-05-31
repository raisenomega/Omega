import { ComingSoon } from "@/components/ComingSoon";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { useProAccess } from "@/hooks/useProAccess";
import { ProFeatureGate, ProGateLoading } from "@/components/ProFeatureGate";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
import { EmptyState } from "@/components/common/EmptyState";

export default function CrisisPage() {
  useTrackOnMount("feature_open", { feature: "crisis_room" });
  const access = useProAccess();
  const { activeBusinessId, isReady } = useActiveBusiness();
  if (access.loading) return <ProGateLoading />;
  if (!access.hasPro)
    return <ProFeatureGate feature="Crisis Room" description="Monitoreo y gestión de crisis de marca." clientId={access.clientId} />;
  if (!isReady) return null;
  if (!activeBusinessId) return <EmptyState feature="Crisis Room" />;
  return (
    <ComingSoon
      title="Crisis Room · Add-on $25/mes"
      message="Monitoreo y gestión de crisis · Disponible próximamente."
    />
  );
}
