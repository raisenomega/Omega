import { useState, useEffect } from "react";
import { Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter,
} from "@/components/ui/dialog";
import { AgentAvatar } from "./AgentAvatar";
import type { Agent } from "./_agents_data";

interface AgentDetailModalProps {
  agent: Agent | null;
  onClose: () => void;
  onActivate: (agentAddonCode: string) => void;  // DEBT-091 · code del tier seleccionado
}

// Modal de detalle del agente · foto grande + header + toggle de tier (Esencial/Pro) ·
// el CTA "Activar Agente" refleja el precio del tier seleccionado.
export function AgentDetailModal({ agent, onClose, onActivate }: AgentDetailModalProps) {
  const [tierIdx, setTierIdx] = useState(0);
  useEffect(() => { setTierIdx(0); }, [agent]);
  if (!agent) return null;
  const tier = agent.tiers[tierIdx] ?? agent.tiers[0];
  const multiTier = agent.tiers.length > 1;

  return (
    <Dialog open={!!agent} onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent className="sm:max-w-2xl">
        <div className="flex flex-col gap-4 sm:flex-row">
          <AgentAvatar
            src={agent.image}
            name={agent.persona}
            className="mx-auto h-28 w-28 shrink-0 rounded-xl border-2 border-amber-500/40 sm:mx-0"
          />
          <DialogHeader className="flex-1">
            <DialogTitle className="text-xl">{agent.persona}</DialogTitle>
            <p className="text-sm text-muted-foreground">
              {agent.role} · <span className="font-semibold text-foreground">{tier.price}</span>
            </p>
            <DialogDescription className="pt-1">{agent.description}</DialogDescription>
          </DialogHeader>
        </div>

        {multiTier && (
          <div className="flex gap-2">
            {agent.tiers.map((t, i) => (
              <button
                key={t.label}
                onClick={() => setTierIdx(i)}
                className={`flex-1 rounded-lg border px-3 py-2 text-xs font-semibold transition-colors duration-200 ${
                  i === tierIdx
                    ? "border-amber-500 bg-amber-500 text-black"
                    : "border-border/40 bg-transparent text-muted-foreground hover:border-amber-500/50"
                }`}
              >
                {t.label} · {t.price}
              </button>
            ))}
          </div>
        )}

        <ul className="space-y-1.5">
          {tier.bullets.map((b) => (
            <li key={b} className="flex gap-2 text-xs text-muted-foreground">
              <Check className="mt-0.5 h-3 w-3 shrink-0 text-emerald-600" />
              <span>{b}</span>
            </li>
          ))}
        </ul>

        <p className="border-t pt-2 text-xs italic text-muted-foreground">
          <span className="font-medium not-italic">Ideal para:</span> {tier.idealFor}
        </p>

        <DialogFooter className="gap-2 sm:gap-2">
          <Button variant="outline" onClick={onClose}>Cerrar</Button>
          <Button onClick={() => onActivate(tier.code)} className="bg-emerald-600 text-white hover:bg-emerald-700">
            Activar Agente · {tier.price}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
