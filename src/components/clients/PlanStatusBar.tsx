import { useNavigate } from "react-router-dom";
import { useClientPlanStatus } from "@/hooks/useClientPlanStatus";
import { useUpgradePlan } from "@/hooks/useUpgradePlan";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Loader2, ArrowUpRight, Lock } from "lucide-react";
import { cn } from "@/lib/utils";
import { NETWORKS, type Network, type PlanCode } from "@/lib/plan-limits";
import { getNetworkIcon } from "@/lib/network-icons";

interface PlanStatusBarProps {
  clientId: string;
}

function Divider() {
  return <div className="h-5 w-px bg-border/60 hidden sm:block" aria-hidden />;
}

// Botón upgrade · cubre tier ordering completo + trial (entrada al selector).
// adopcion → "Elegí tu plan" lleva a /settings (PlanSection · sin saltar a basic).
// basic → pro · pro → enterprise · enterprise → sin CTA (plan máximo).
type UpgradeCta =
  | { label: string; kind: "navigate"; to: string }
  | { label: string; kind: "checkout"; targetPlan: "basic" | "pro" | "enterprise" }
  | null;

function getUpgradeCta(planCode: PlanCode): UpgradeCta {
  if (planCode === "adopcion") return { label: "Elegí tu plan", kind: "navigate", to: "/settings" };
  if (planCode === "basic") return { label: "Subir a PRO", kind: "checkout", targetPlan: "pro" };
  if (planCode === "pro") return { label: "Subir a Enterprise", kind: "checkout", targetPlan: "enterprise" };
  return null;
}

// Display de renovación · 7 estados legibles (cuentas perpetuas ocultas).
// Trial >3d ámbar · ≤3d rojo · vencido rojo+CTA · plan ≤30d días · 31-365d fecha · perpetuo null.
type RenewalTone = "muted" | "amber" | "destructive";
type RenewalDisplay = { text: string; tone: RenewalTone } | null;

function getRenewalDisplay(planCode: PlanCode, renewsOn: string | null): RenewalDisplay {
  if (!renewsOn) return null;
  const days = Math.ceil((new Date(renewsOn).getTime() - Date.now()) / 86400000);
  if (planCode === "adopcion") {
    if (days <= 0) return { text: "Trial vencido · elegí tu plan", tone: "destructive" };
    return { text: `Trial · ${days}d restantes`, tone: days <= 3 ? "destructive" : "amber" };
  }
  if (days <= 0) return { text: "Venció · renovar ahora", tone: "destructive" };
  if (days > 365) return null;
  if (days <= 30) return { text: `Renueva en ${days}d`, tone: "muted" };
  const fmt = new Intl.DateTimeFormat("es-AR", { day: "numeric", month: "short" }).format(new Date(renewsOn));
  return { text: `Renueva ${fmt}`, tone: "muted" };
}

const RENEWAL_TONE_CLASS: Record<RenewalTone, string> = {
  muted: "text-muted-foreground",
  amber: "text-amber-500 font-medium",
  destructive: "text-destructive font-medium",
};

export function PlanStatusBar({ clientId }: PlanStatusBarProps) {
  const status = useClientPlanStatus(clientId);
  const upgradeMutation = useUpgradePlan();
  const navigate = useNavigate();

  if (status.loading) {
    return (
      <Card className="flex items-center justify-center py-3 border-2 border-warning bg-card/80 backdrop-blur-sm">
        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
      </Card>
    );
  }

  // Bar siempre se renderiza (incluso pre-activación · status devuelve defaults de Adopción).
  // Cuando cliente activa plan, los números se actualizan reactivamente sin remontaje.
  const { planConfig, postsUsed, postsTotal, percentUsed, accountsByNetwork, features, renewsOn } = status;
  const renewalDisplay = getRenewalDisplay(planConfig.code, renewsOn);
  const upgradeCta = getUpgradeCta(planConfig.code);

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
            <span className="text-muted-foreground tabular-nums">{postsUsed}/{postsTotal} posts</span>
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
          <span className="text-xs text-muted-foreground tabular-nums whitespace-nowrap">
            {NETWORKS.filter((n) => accountsByNetwork[n].active).length}/{planConfig.accountsPerNetwork} ctas
          </span>
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

        {/* Lock badge · solo plan=basic con features bloqueadas · indicador upgrade */}
        {planConfig.code === "basic" && features.locked.length > 0 && (
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="inline-flex items-center gap-0.5 text-xs text-muted-foreground cursor-help tabular-nums">
                <Lock className="h-3 w-3" />
                {features.locked.length}
              </span>
            </TooltipTrigger>
            <TooltipContent className="max-w-xs">
              {features.locked.map((f) => f.label).join(" · ")} — disponibles en PRO
            </TooltipContent>
          </Tooltip>
        )}

        {/* Renewal display · 7 estados · ver getRenewalDisplay */}
        {renewalDisplay && (
          <span className={cn("whitespace-nowrap sm:ml-auto", RENEWAL_TONE_CLASS[renewalDisplay.tone])}>
            {renewalDisplay.text}
          </span>
        )}

        {/* Upgrade CTA · tier ordering completo · trial → /settings (selector de planes) */}
        {upgradeCta && (
          <Button
            size="sm"
            className={cn("h-7 whitespace-nowrap", !renewalDisplay && "sm:ml-auto")}
            disabled={upgradeMutation.isPending}
            onClick={() => {
              if (upgradeCta.kind === "navigate") {
                navigate(upgradeCta.to);
              } else {
                upgradeMutation.mutate({ clientId, targetPlan: upgradeCta.targetPlan });
              }
            }}
          >
            {upgradeMutation.isPending ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <>
                <ArrowUpRight className="h-3.5 w-3.5" />
                {upgradeCta.label}
              </>
            )}
          </Button>
        )}
      </Card>
    </TooltipProvider>
  );
}
