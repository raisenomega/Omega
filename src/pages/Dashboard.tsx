import { Users, Sparkles, CalendarDays, Wifi, Loader2 } from "lucide-react";
import { useDashboardData } from "@/hooks/useDashboardData";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { AccountDistributionChart } from "@/components/dashboard/PlatformCharts";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { PlatformStatus } from "@/components/dashboard/PlatformStatus";

export default function Dashboard() {
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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-display font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Resumen general de tu plataforma</p>
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

      {/* Distribución de cuentas (única chart con data real) */}
      <AccountDistributionChart data={platformCounts} />

      {/* Activity + Platform Status */}
      <div className="grid gap-4 lg:grid-cols-2">
        <ActivityFeed recentClients={recentClients} recentAccounts={recentAccounts} />
        <PlatformStatus data={platformCounts} />
      </div>
    </div>
  );
}
