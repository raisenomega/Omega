import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useAgentActivity } from "@/hooks/useAgentActivity";

const AGENT_LABELS: Record<string, string> = {
  content_creator: "Creador de Contenido",
  trend_hunter: "Cazador de Tendencias",
  brand_voice: "Voz de Marca",
  publisher: "Publicador",
};

const AGENT_COLORS: Record<string, string> = {
  content_creator: "hsl(265, 75%, 60%)",
  trend_hunter: "hsl(160, 70%, 45%)",
  brand_voice: "hsl(35, 85%, 55%)",
  publisher: "hsl(200, 80%, 50%)",
};

const FALLBACK_COLORS = [
  "hsl(340, 75%, 55%)",
  "hsl(90, 60%, 50%)",
  "hsl(220, 70%, 60%)",
  "hsl(0, 0%, 60%)",
];

function labelFor(code: string): string {
  return AGENT_LABELS[code] || code;
}

function colorFor(code: string, index: number): string {
  return AGENT_COLORS[code] || FALLBACK_COLORS[index % FALLBACK_COLORS.length];
}

export function AgentActivityChart() {
  const { data, agentCodes, isLoading } = useAgentActivity();

  if (!isLoading && agentCodes.length === 0) {
    return (
      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-lg">Actividad de Agentes</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-12">
          <p className="text-sm text-muted-foreground">
            Sin actividad de agentes en los últimos 7 días
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-lg">Actividad de Agentes</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="day" tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                color: "hsl(var(--foreground))",
              }}
              itemStyle={{ color: "#fff" }}
              labelStyle={{ color: "#fff" }}
              formatter={(value: number, name: string) => [value ?? 0, labelFor(name)]}
            />
            <Legend formatter={(value: string) => labelFor(value)} wrapperStyle={{ fontSize: 12 }} />
            {agentCodes.map((code, i) => (
              <Bar key={code} dataKey={code} fill={colorFor(code, i)} radius={[4, 4, 0, 0]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
