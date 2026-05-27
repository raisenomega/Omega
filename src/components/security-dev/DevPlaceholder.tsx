// Placeholder honesto (DEBT-106 Sprint 8): muestra el estado real de las 4 keys
// en Railway. Sin spinners eternos · sin "coming soon" vacío. Íconos Lucide (no emoji).
import { Check, X, type LucideIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useDevHealth, type DevHealth } from "@/hooks/useSecurityDevData";

const KEYS: { id: keyof Omit<DevHealth, "all_ready">; label: string }[] = [
  { id: "e2b_api_key", label: "E2B_API_KEY" },
  { id: "railway_api_token", label: "RAILWAY_API_TOKEN" },
  { id: "railway_project_id", label: "RAILWAY_PROJECT_ID" },
  { id: "github_token", label: "GITHUB_TOKEN" },
];

export function DevPlaceholder({ icon: Icon, title, description }: {
  icon: LucideIcon; title: string; description?: string;
}) {
  const { data, isLoading, error } = useDevHealth();
  if (isLoading) return <Skeleton className="h-48 w-full" />;
  const err = (error as Error)?.message;
  if (err) return <p className="text-sm text-red-500">Error: {err}</p>;
  const h = data!;
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Icon className="h-5 w-5" /> {title}
          <Badge variant="outline" className="ml-auto border-violet-500/40 bg-violet-500/15 text-violet-400">PRÓXIMAMENTE</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
        <ul className="space-y-1">
          {KEYS.map((k) => (
            <li key={k.id} className="flex items-center gap-2 text-sm">
              {h[k.id] ? <Check className="h-4 w-4 text-green-500" /> : <X className="h-4 w-4 text-red-500" />}
              <span className={h[k.id] ? "" : "text-muted-foreground"}>{k.label}</span>
            </li>
          ))}
        </ul>
        <p className="text-sm font-medium">
          {h.all_ready ? "Backend listo · disponible en Sprint 8" : "Carga las keys faltantes en Railway para activar"}
        </p>
      </CardContent>
    </Card>
  );
}
