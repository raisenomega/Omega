import { useMyPlanStatus } from "@/hooks/useMyPlanStatus";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { ProfileSection } from "@/components/settings/ProfileSection";
import { PlanSection } from "@/components/settings/PlanSection";
import { PaymentSection } from "@/components/settings/PaymentSection";

// DEBT-033 parcial: SettingsPage V3 reescrita · sustituye ComingSoon.
// Cubre: Profile (name/industry/region · PATCH /clients/profile) + Plan
// (useClientPlanStatus + useUpgradePlan reusados) + Payment (placeholder
// DEBT-038). NO usa profiles/organizations/user_roles/audit_logs.
export default function SettingsPage() {
  const my = useMyPlanStatus();
  useTrackOnMount("feature_open", { feature: "settings" });

  return (
    <div className="container mx-auto max-w-3xl px-4 py-8 space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold">Configuración</h1>
        <p className="text-sm text-muted-foreground">Perfil del negocio, plan y método de pago.</p>
      </header>

      <ProfileSection />
      <PlanSection clientId={my.clientId} />
      <PaymentSection />
    </div>
  );
}
