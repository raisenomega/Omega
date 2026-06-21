import { Users, Sparkles, CalendarDays, Wifi, Loader2 } from "lucide-react";
import { useDashboardData } from "@/hooks/useDashboardData";
import { useMyPlanStatus } from "@/hooks/useMyPlanStatus";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";
import { useTrackOnMount } from "@/hooks/useBehavioralTracking";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { AccountDistributionChart } from "@/components/dashboard/PlatformCharts";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { PlatformStatus } from "@/components/dashboard/PlatformStatus";
import { SecurityKPICard } from "@/components/dashboard/SecurityKPICard";
import { AriaSuggestionsCard } from "@/components/dashboard/AriaSuggestionsCard";
import { AgentActivityChart } from "@/components/dashboard/AgentActivityChart";
import { ObservationsFeed } from "@/components/dashboard/ObservationsFeed";
import { SentinelDashboardCard } from "@/components/dashboard/SentinelDashboardCard";
import { PlanStatusBar } from "@/components/clients/PlanStatusBar";

export default function Dashboard() {
  useTrackOnMount("feature_open", { feature: "dashboard" });

  const {
    loading,
    activeClients,
    totalClients,
    activeAccounts,
    totalAccounts,
    scheduledNext7d,
    contentLast30d,
    platformCounts,
    recentClients,
    recentAccounts,
  } = useDashboardData();

  const myPlan = useMyPlanStatus();
  // Negocio activo del Switcher (reseller elige · cliente N=1 auto-selecciona) o cliente propio.
  // Universal: los 3 elementos base (barra/seguridad/ARIA) se scopean a ESTE negocio, no al rol.
  const { activeBusinessId } = useActiveBusiness();
  const businessId = activeBusinessId ?? myPlan.clientId;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header inline · título + Plan Status Bar en misma línea horizontal.
          Universal: barra del NEGOCIO ACTIVO (cualquier usuario). Gateada por businessId
          (no por rol) → sin negocio seleccionado no muestra Adopción falsa. En mobile
          flex-wrap lo baja a línea propia automáticamente. */}
      <div className="flex items-center justify-between gap-6 flex-wrap">
        <div className="shrink-0">
          <h1 className="text-2xl font-display font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Resumen general de tu plataforma</p>
        </div>
        {businessId && (
          <div className="flex-1 min-w-[420px]">
            <PlanStatusBar clientId={businessId} />
          </div>
        )}
      </div>

      {/* KPI Cards — datos reales (regla P1) */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Clientes Activos"
          value={activeClients}
          icon={Users}
          subtitle={`${totalClients} total`}
        />
        <StatsCard
          title="Contenido Generado"
          value={contentLast30d}
          icon={Sparkles}
          subtitle="Últimos 30 días"
        />
        <StatsCard
          title="Posts Programados"
          value={scheduledNext7d}
          icon={CalendarDays}
          subtitle="Próximos 7 días"
        />
        <StatsCard
          title="Cuentas Conectadas"
          value={`${activeAccounts}/${totalAccounts}`}
          icon={Wifi}
          subtitle={`${totalAccounts} registradas`}
        />
      </div>

      {/* Universal (cualquier usuario): seguridad de la SESIÓN (per-usuario) + sugerencias de ARIA
          del NEGOCIO ACTIVO. Sin gate de rol · ARIA con businessId null muestra su empty honesto. */}
      <div className="grid gap-4 lg:grid-cols-2">
        <SecurityKPICard />
        <AriaSuggestionsCard clientId={businessId} />
      </div>

      {/* CAMBIO 3+4 · actividad de agentes · distribución de cuentas (donut) · observaciones — mismo nivel */}
      <div className="grid gap-4 lg:grid-cols-3">
        <AgentActivityChart />
        <AccountDistributionChart data={platformCounts} />
        <ObservationsFeed clientId={myPlan.clientId ?? null} />
      </div>

      {/* Activity + Platform Status */}
      <div className="grid gap-4 lg:grid-cols-2">
        <ActivityFeed recentClients={recentClients} recentAccounts={recentAccounts} />
        {/* SENTINEL 4B-5 · solo superadmin real (is_owner=true) ve salud del sistema · resto ve estado por plataforma */}
        {myPlan.isSuperadmin ? <SentinelDashboardCard /> : <PlatformStatus data={platformCounts} />}
      </div>
    </div>
  );
}
