import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

interface AgentRow {
  agent_code: string;
  created_at: string;
}

export interface AgentActivityBucket {
  day: string;
  [agentCode: string]: string | number;
}

const DAY_LABELS = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"] as const;

function startOfDay(d: Date): Date {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  return x;
}

function bucketLabel(d: Date): string {
  return `${DAY_LABELS[d.getDay()]} ${d.getDate()}`;
}

export function useAgentActivity() {
  const query = useQuery({
    queryKey: ["content_lab_generated", "agent_activity_7d"],
    queryFn: async (): Promise<AgentRow[]> => {
      const since = startOfDay(new Date());
      since.setDate(since.getDate() - 6); // 7 buckets: hoy + 6 días atrás
      const { data, error } = await supabase
        .from("content_lab_generated")
        .select("agent_code, created_at")
        .gte("created_at", since.toISOString());
      if (error) throw error;
      return (data ?? []) as AgentRow[];
    },
  });

  const rows = query.data ?? [];

  // 7 buckets de día (hoy + 6 atrás), índice 0 = más antiguo
  const today = startOfDay(new Date());
  const days: Date[] = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(today);
    d.setDate(d.getDate() - (6 - i));
    return d;
  });
  const dayKeys = days.map((d) => startOfDay(d).getTime());

  // agentCodes REALES presentes en los datos (no fijamos 4)
  const agentCodes = Array.from(new Set(rows.map((r) => r.agent_code))).sort();

  const buckets: AgentActivityBucket[] = days.map((d) => {
    const base: AgentActivityBucket = { day: bucketLabel(d) };
    for (const code of agentCodes) base[code] = 0;
    return base;
  });

  for (const row of rows) {
    const dayTs = startOfDay(new Date(row.created_at)).getTime();
    const idx = dayKeys.indexOf(dayTs);
    if (idx < 0) continue; // fuera de la ventana de 7 días
    const current = buckets[idx][row.agent_code];
    buckets[idx][row.agent_code] = (typeof current === "number" ? current : 0) + 1;
  }

  return { data: buckets, agentCodes, isLoading: query.isLoading };
}
