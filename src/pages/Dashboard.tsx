import { Users, TrendingUp, CalendarDays, Wifi, Loader2 } from "lucide-react";
import { useDashboardData } from "@/hooks/useDashboardData";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { FollowersByPlatformChart, AccountDistributionChart } from "@/components/dashboard/PlatformCharts";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";
import { PlatformStatus } from "@/components/dashboard/PlatformStatus";

export default function Dashboard() {
  const {
    loading,
    activeClients,
    totalFollowers,
    connectedAccounts,
    totalAccounts,
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

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Clientes Activos"
          value={activeClients}
          icon={Users}
          subtitle={`${activeClients} de ${activeClients} activos`}
        />
        <StatsCard
          title="Seguidores Totales"
          value={totalFollowers.toLocaleString()}
          icon={TrendingUp}
          subtitle="Todas las plataformas"
        />
        <StatsCard
          title="Posts Programados"
          value="0"
          icon={CalendarDays}
          subtitle="Próximamente"
        />
        <StatsCard
          title="Cuentas Conectadas"
          value={`${connectedAccounts}/${totalAccounts}`}
          icon={Wifi}
          subtitle={`${totalAccounts} cuentas registradas`}
        />
      </div>

      {/* Charts */}
      <div className="grid gap-4 lg:grid-cols-2">
        <FollowersByPlatformChart data={platformCounts} />
        <AccountDistributionChart data={platformCounts} />
      </div>

      {/* Activity + Platform Status */}
      <div className="grid gap-4 lg:grid-cols-2">
        <ActivityFeed recentClients={recentClients} recentAccounts={recentAccounts} />
        <PlatformStatus data={platformCounts} />
      </div>
    </div>
  );
}
