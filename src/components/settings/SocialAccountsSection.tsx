import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { apiGet } from "@/lib/api-client";
import { PLATFORMS, PLATFORM_LABELS, PLATFORM_COLORS, type Platform } from "@/lib/onboarding-constants";

interface Acc {
  platform: string;
  username?: string;
  is_paused?: boolean;
}
interface OnboardingResp {
  social_accounts?: Acc[];
}

interface Status { kind: "not_connected" | "connected" | "expired"; username?: string }

const STATUS_BADGE: Record<Status["kind"], { label: string; color: string }> = {
  not_connected: { label: "No conectada", color: "bg-muted text-muted-foreground" },
  connected: { label: "Conectada", color: "bg-emerald-500 text-white" },
  expired: { label: "Token expirado", color: "bg-rose-500 text-white" },
};

// DEBT-CL-021 cerrada: apiGet fuente única auth + apiBase.
const fetchData = (clientId: string) => apiGet<OnboardingResp>(`/clients/${clientId}/onboarding-data`);

interface SocialAccountsSectionProps { clientId: string | null }

export function SocialAccountsSection({ clientId }: SocialAccountsSectionProps) {
  const q = useQuery({ queryKey: ["onboarding-social", clientId], queryFn: () => fetchData(clientId!), enabled: !!clientId });
  const accounts: Acc[] = q.data?.social_accounts ?? [];
  const byPlatform = new Map<string, Acc>();
  for (const a of accounts) byPlatform.set(a.platform, a);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Conexiones de plataformas</CardTitle>
        <p className="text-xs text-muted-foreground">Conecta tus cuentas de negocio para que ARIA pueda publicar y analizar métricas en tiempo real.</p>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {PLATFORMS.map((p) => {
            const acc = byPlatform.get(p);
            const status: Status["kind"] = acc ? "connected" : "not_connected";
            const b = STATUS_BADGE[status];
            return (
              <div key={p} className="border border-border/40 rounded-lg p-2.5 flex items-center gap-2.5">
                <span className="h-3 w-3 rounded-full shrink-0" style={{ background: PLATFORM_COLORS[p as Platform] }} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{PLATFORM_LABELS[p as Platform]}</p>
                  <p className="text-[10px] text-muted-foreground truncate">{acc?.username ?? "—"}</p>
                </div>
                <Badge className={`${b.color} text-[10px] h-5 px-1.5 shrink-0`}>{b.label}</Badge>
                <Button size="sm" variant="outline" disabled className="h-7 text-xs shrink-0" title="DEBT-040 · OAuth Fase 2">
                  {status === "connected" ? "Desconectar" : "Conectar"}
                </Button>
              </div>
            );
          })}
        </div>
        <p className="text-[10px] text-muted-foreground pt-1">Las conexiones OAuth con Meta Business, TikTok for Business y YouTube se activarán en la próxima actualización.</p>
      </CardContent>
    </Card>
  );
}
