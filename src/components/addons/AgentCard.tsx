import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AgentAvatar } from "./AgentAvatar";
import type { Agent } from "./_agents_data";

interface AgentCardProps {
  agent: Agent;
  onOpen: () => void;
}

// Card compacta del agente · clic → AgentDetailModal. Botón ghost amber→emerald (patrón Add-Ons).
export function AgentCard({ agent, onOpen }: AgentCardProps) {
  const price = agent.tiers.length > 1 ? `desde ${agent.tiers[0].price}` : agent.tiers[0].price;
  return (
    <Card className="flex flex-col h-full">
      <CardContent className="flex flex-col items-center gap-3 p-5 flex-1 text-center">
        <AgentAvatar
          src={agent.image}
          name={agent.persona}
          className="h-24 w-24 rounded-full border-2 border-amber-500/40"
        />
        <div>
          <h3 className="text-lg font-bold leading-tight">{agent.persona}</h3>
          <p className="text-xs text-muted-foreground">{agent.role}</p>
        </div>
        <p className="flex-1 text-xs text-muted-foreground">{agent.tagline}</p>
        <span className="text-base font-bold">{price}</span>
        <Button
          onClick={onOpen}
          className="w-full border border-amber-500 bg-transparent text-white transition-colors duration-200 hover:bg-emerald-600 hover:border-emerald-600 hover:text-white"
        >
          Conocer Agente →
        </Button>
      </CardContent>
    </Card>
  );
}
