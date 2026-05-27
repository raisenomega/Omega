import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Bot, ArrowRight, Loader2 } from "lucide-react";
import { useClientActiveAgents } from "@/hooks/useClientActiveAgents";
import type { Agent } from "@/components/addons/_agents_data";

function AgentCard({ agent }: { agent: Agent }) {
  const [imgFailed, setImgFailed] = useState(false);
  return (
    <div className="flex items-start gap-3 rounded-lg border border-border/30 bg-muted/20 p-3">
      <div className="relative shrink-0">
        {imgFailed ? (
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
            <Bot className="h-6 w-6 text-muted-foreground" />
          </div>
        ) : (
          <img
            src={agent.image}
            alt={agent.persona}
            className="h-12 w-12 rounded-full object-cover"
            onError={() => setImgFailed(true)}
          />
        )}
        <span className="absolute bottom-0 right-0 h-2 w-2 rounded-full bg-emerald-500 ring-2 ring-card" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium">
          {agent.role} <span className="text-muted-foreground">· {agent.persona}</span>
        </p>
        <p className="mt-0.5 text-xs text-muted-foreground line-clamp-2">{agent.tagline}</p>
      </div>
    </div>
  );
}

interface ClientAgentsActiveProps {
  clientId: string;
}

export function ClientAgentsActive({ clientId }: ClientAgentsActiveProps) {
  const navigate = useNavigate();
  const { agents, isLoading } = useClientActiveAgents(clientId);

  return (
    <Card className="border-border/50 bg-card/60">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm font-medium">
          <Bot className="h-4 w-4" /> Agentes activos
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex justify-center py-4">
            <Loader2 className="h-5 w-5 animate-spin text-primary" />
          </div>
        ) : agents.length > 0 ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {agents.map((agent) => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3 py-6 text-center">
            <p className="text-xs text-muted-foreground">
              Este cliente no tiene agentes activos todavía.
            </p>
            <Button
              size="sm"
              onClick={() => navigate("/add-ons#agentes")}
              className="border border-amber-500 bg-transparent text-white transition-colors duration-200 hover:bg-emerald-600 hover:border-emerald-600 hover:text-white"
            >
              Explorar Agentes <ArrowRight className="ml-1 h-3.5 w-3.5" />
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
