// DEBT-052 · widget de créditos prepagados (Tab Agente · columna derecha).
// Con pack: saldo (barra) + consumido + periodo + toggle auto-recarga + consumo por agente.
// Sin pack: "Sin pack activo" + botón "Añadir Créditos" → CreditPackModal → Stripe.
// Cero mocks — datos reales de client_agent_credits / client_credit_ledger (RLS client-scoped).
// Caveat: compra + toggle son self-service (cliente por JWT) · sirven para self-view/demo.

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Loader2, Wallet, Bot, RefreshCw, Coins } from "lucide-react";
import { useClientCredits } from "@/hooks/useClientCredits";
import { useAutoRechargeToggle } from "@/hooks/useAutoRechargeToggle";
import { CreditPackModal } from "@/components/clients/CreditPackModal";

function usd(n: number): string {
  return `$${n.toFixed(2)}`;
}

function fmtDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" });
}

interface Props {
  clientId: string;
}

export function ClientCreditsWidget({ clientId }: Props) {
  const c = useClientCredits(clientId);
  const toggle = useAutoRechargeToggle(clientId);

  return (
    <Card className="border-border/50 bg-card/60">
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-sm font-medium">
          <span className="flex items-center gap-2">
            <Coins className="h-4 w-4" /> Añade Créditos por tu consumo
          </span>
          {c.enrolled && c.tier && (
            <Badge variant="secondary" className="capitalize text-xs">{c.tier}</Badge>
          )}
        </CardTitle>
        <p className="text-xs text-muted-foreground">
          Amplía tu capacidad de generación cuando lo necesites · sin cambiar tu plan · Usalos como quieras y cancela cuando quieras.
        </p>
      </CardHeader>
      <CardContent>
        {c.isLoading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-5 w-5 animate-spin text-primary" />
          </div>
        ) : c.isError ? (
          <p className="text-xs text-destructive text-center py-8">
            Error al cargar los créditos. Recargá la página.
          </p>
        ) : !c.enrolled ? (
          <div className="space-y-3 py-2">
            <p className="text-xs text-muted-foreground text-center">Sin pack activo.</p>
            <CreditPackModal />
          </div>
        ) : (
          <div className="space-y-4">
            {/* Saldo / budget */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <Wallet className="h-3.5 w-3.5" /> Saldo del periodo
                </span>
                <span className="font-semibold tabular-nums">
                  {usd(c.saldoUsd)} <span className="text-muted-foreground font-normal">/ {usd(c.budgetUsd)}</span>
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${c.pctUsed}%` }} />
              </div>
              <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                <span>Consumido {usd(c.consumidoUsd)} ({c.pctUsed}%)</span>
                <span>Renueva {fmtDate(c.periodoEnd)}</span>
              </div>
            </div>

            {/* Auto-recarga · toggle interactivo */}
            <div className="flex items-center gap-2 border-t border-border/20 pt-3 text-xs">
              <RefreshCw className="h-3.5 w-3.5 text-muted-foreground" />
              <span className="text-muted-foreground">Auto-recarga</span>
              <Switch
                className="ml-auto"
                checked={c.autoRecharge}
                disabled={toggle.isPending}
                onCheckedChange={(v) => toggle.mutate(v)}
              />
            </div>

            {/* Consumo por agente */}
            <div className="border-t border-border/20 pt-3">
              <p className="text-xs font-medium mb-2 flex items-center gap-1.5">
                <Bot className="h-3.5 w-3.5" /> Consumo por agente
              </p>
              {c.consumption.length === 0 ? (
                <p className="text-[11px] text-muted-foreground">Sin consumo registrado en este periodo.</p>
              ) : (
                <div className="space-y-1.5">
                  {c.consumption.map((a) => (
                    <div key={a.agentCode} className="flex items-center justify-between text-xs">
                      <span className="truncate">{a.agentName}</span>
                      <span className="text-muted-foreground tabular-nums">{usd(a.totalUsd)} · {a.count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
