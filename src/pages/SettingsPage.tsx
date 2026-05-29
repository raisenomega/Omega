import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useMyPlanStatus } from "@/hooks/useMyPlanStatus";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { ProfileSection } from "@/components/settings/ProfileSection";
import { PlanSection } from "@/components/settings/PlanSection";
import { PaymentSection } from "@/components/settings/PaymentSection";
import { ARIASection } from "@/components/settings/ARIASection";
import { SocialAccountsSection } from "@/components/settings/SocialAccountsSection";
import { ConnectMetaButton } from "@/components/integrations/ConnectMetaButton";
import { ConnectGoogleButton } from "@/components/integrations/ConnectGoogleButton";
import { SecuritySection } from "@/components/settings/SecuritySection";
import { NotificationsSection } from "@/components/settings/NotificationsSection";

type TabId = "perfil" | "plan" | "aria" | "cuentas" | "seguridad" | "notificaciones";

const TABS: { id: TabId; label: string }[] = [
  { id: "perfil", label: "Perfil" },
  { id: "plan", label: "Plan" },
  { id: "aria", label: "ARIA" },
  { id: "cuentas", label: "Cuentas" },
  { id: "seguridad", label: "Seguridad" },
  { id: "notificaciones", label: "Notificaciones" },
];

export default function SettingsPage() {
  const my = useMyPlanStatus();
  const [params] = useSearchParams();
  const tab = params.get("tab");
  const [active, setActive] = useState<TabId>(
    TABS.some((t) => t.id === tab) ? (tab as TabId) : "perfil",
  );
  useTrackOnMount("feature_open", { feature: "settings" });

  return (
    <div className="container mx-auto max-w-3xl px-4 py-6 space-y-4">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold">Configuración</h1>
      </header>

      <div className="flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setActive(t.id)}
            className={cn(
              "rounded-full px-3 py-1 text-xs border transition cursor-pointer",
              active === t.id
                ? "bg-primary text-primary-foreground border-primary"
                : "bg-muted/40 text-muted-foreground border-border/50 hover:bg-muted/60",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {active === "perfil" && <ProfileSection />}
      {active === "plan" && (<div className="space-y-4"><PlanSection clientId={my.clientId} /><PaymentSection /></div>)}
      {active === "aria" && <ARIASection />}
      {active === "cuentas" && (
        <div className="space-y-4">
          {/* RONDA D · OAuth · conectar Meta + Google (503 honesto sin credenciales) */}
          <div className="flex flex-wrap gap-2">
            <ConnectMetaButton />
            <ConnectGoogleButton />
          </div>
          <SocialAccountsSection clientId={my.clientId} />
        </div>
      )}
      {active === "seguridad" && <SecuritySection />}
      {active === "notificaciones" && <NotificationsSection clientId={my.clientId} />}
    </div>
  );
}
