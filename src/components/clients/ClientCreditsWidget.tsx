// DEBT-052 FASE 5 · AI Tab · widget de créditos prepagados del cliente.
// Budget + saldo (barra) + periodo + pack activo + auto-recarga + consumo por agente.
// Cero mocks — datos reales de client_agent_credits / client_credit_ledger (RLS client-scoped).

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Wallet, Bot, RefreshCw, Coins } from "lucide-react";
import { useClientCredits } from "@/hooks/useClientCredits";

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

  return (
    <Card className="border-border/50 bg-card/60">
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-sm font-medium">
          <span className="flex items-center gap-2">
            <Coins className="h-4 w-4" /> Créditos prepagados
          </span>
          {c.enrolled && c.tier && (
            <Badge variant="secondary" className="capitalize text-xs">{c.tier}</Badge>
          )}
        </CardTitle>
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
          <p className="text-xs text-muted-foreground text-center py-8">
            Este cliente no tiene un Credit Pack activo.
          </p>
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

            {/* Auto-recarga */}
            <div className="flex items-center gap-2 border-t border-border/20 pt-3 text-xs">
              <RefreshCw className="h-3.5 w-3.5 text-muted-foreground" />
              <span className="text-muted-foreground">Auto-recarga:</span>
              <Badge variant={c.autoRecharge ? "default" : "outline"} className="text-[10px] px-1.5 py-0">
                {c.autoRecharge ? "Activada" : "Desactivada"}
              </Badge>
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
