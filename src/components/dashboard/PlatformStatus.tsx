import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getNetworkIcon } from "@/lib/network-icons";

interface PlatformData {
  platform: string;
  count: number;
  activeCount: number;
}

const PLATFORM_LABELS: Record<string, string> = {
  instagram: "Instagram",
  facebook: "Facebook",
  tiktok: "TikTok",
  twitter: "X / Twitter",
  linkedin: "LinkedIn",
  youtube: "YouTube",
};

interface PlatformStatusProps {
  data: PlatformData[];
}

export function PlatformStatus({ data }: PlatformStatusProps) {
  const hasAny = data.some((d) => d.count > 0);

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="text-lg">Estado por Plataforma</CardTitle>
      </CardHeader>
      <CardContent>
        {!hasAny ? (
          <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
            <p className="text-sm">Sin cuentas conectadas</p>
            <p className="text-xs mt-1">Conecta cuentas de tus clientes</p>
          </div>
        ) : (
          <div className="space-y-3">
            {data
              .filter((d) => d.count > 0)
              .map((d) => {
                const { icon: Icon } = getNetworkIcon(d.platform);
                const label = PLATFORM_LABELS[d.platform] ?? d.platform;
                return (
                  <div
                    key={d.platform}
                    className="flex items-center gap-3 rounded-lg border border-border/30 bg-muted/30 p-3"
                  >
                    <Icon className="h-5 w-5 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{label}</p>
                      <p className="text-xs text-muted-foreground">
                        {d.activeCount}/{d.count} {d.count === 1 ? "activa" : "activas"}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        {d.count} {d.count === 1 ? "cuenta" : "cuentas"}
                      </Badge>
                      {d.activeCount > 0 && (
                        <div className="h-2 w-2 rounded-full bg-success" />
                      )}
                    </div>
                  </div>
                );
              })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
