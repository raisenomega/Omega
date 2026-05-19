import { useClientPlanStatus } from "@/hooks/useClientPlanStatus";
import { Card } from "@/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { NETWORKS, type Network } from "@/lib/plan-limits";
import { getNetworkIcon } from "@/lib/network-icons";

interface PlanStatusBarProps {
  clientId: string;
}

function Divider() {
  return <div className="h-5 w-px bg-border/60 hidden sm:block" aria-hidden />;
}

export function PlanStatusBar({ clientId }: PlanStatusBarProps) {
  const status = useClientPlanStatus(clientId);

  if (status.loading) {
    return (
      <Card className="flex items-center justify-center py-3 border-2 border-warning bg-card/80 backdrop-blur-sm">
        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
      </Card>
    );
  }

  // Bar siempre se renderiza (incluso pre-activación · status devuelve defaults de Adopción).
  // Cuando cliente activa plan, los números se actualizan reactivamente sin remontaje.
  const { planConfig, postsUsed, postsTotal, percentUsed, accountsByNetwork, features, renewsInDays } = status;

  const barColor =
    percentUsed >= 95 ? "bg-destructive" :
    percentUsed >= 80 ? "bg-warning" :
    "bg-success";

  return (
    <TooltipProvider delayDuration={300}>
      <Card className="flex flex-wrap items-center gap-3 px-4 py-2.5 border-2 border-warning bg-card/80 backdrop-blur-sm text-sm">
        {/* Plan badge */}
        <span className="font-semibold whitespace-nowrap">
          {planConfig.label}
          <span className="ml-1.5 text-muted-foreground font-normal">· {planConfig.priceLabel}</span>
        </span>

        <Divider />

        {/* Posts progress */}
        {postsTotal > 0 ? (
          <div className="flex items-center gap-2 whitespace-nowrap">
            <span className="text-muted-foreground tabular-nums">{postsUsed}/{postsTotal}</span>
            <div className="h-1.5 w-20 rounded-full bg-muted overflow-hidden">
              <div className={cn("h-full transition-all", barColor)} style={{ width: `${percentUsed}%` }} />
            </div>
            <span className="text-xs text-muted-foreground tabular-nums">{percentUsed}%</span>
          </div>
        ) : (
          <span className="text-muted-foreground whitespace-nowrap">Posts ilimitados</span>
        )}

        <Divider />

        {/* Platform icons */}
        <div className="flex items-center gap-2.5">
          {NETWORKS.map((network) => {
            const { icon: Icon, label } = getNetworkIcon(network);
            const state = accountsByNetwork[network];
            return (
              <Tooltip key={network}>
                <TooltipTrigger asChild>
                  <Icon
                    className={cn(
                      "h-4 w-4 transition-opacity cursor-help",
                      state.active ? "text-foreground opacity-100" : "text-muted-foreground opacity-40"
                    )}
                  />
                </TooltipTrigger>
                <TooltipContent>
                  {label} · {state.active ? "Conectada" : state.exists ? "Inactiva" : "Sin conectar"}
                </TooltipContent>
              </Tooltip>
            );
          })}
        </div>

        <Divider />

        {/* Features count with tooltip */}
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="text-muted-foreground whitespace-nowrap cursor-help">
              {features.unlocked.length}/{features.unlocked.length + features.locked.length} funciones
            </span>
          </TooltipTrigger>
          <TooltipContent className="max-w-xs">
            <div className="space-y-1 text-xs">
              <div>
                <span className="font-semibold">Activas:</span>{" "}
                {features.unlocked.map((f) => f.label).join(", ")}
              </div>
              {features.locked.length > 0 && (
                <div>
                  <span className="font-semibold">Bloqueadas:</span>{" "}
                  {features.locked.map((f) => f.label).join(", ")}
                </div>
              )}
            </div>
          </TooltipContent>
        </Tooltip>

        {/* Renewal pushed to the right */}
        <span className="text-muted-foreground whitespace-nowrap sm:ml-auto">
          {renewsInDays !== null ? `Renueva ${renewsInDays}d` : "Sin renovación"}
        </span>
      </Card>
    </TooltipProvider>
  );
}
