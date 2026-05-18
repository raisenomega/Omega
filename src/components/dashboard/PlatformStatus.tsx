import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface PlatformData {
  platform: string;
  count: number;
  followers: number;
  connected: number;
}

const PLATFORM_CONFIG: Record<string, { label: string; emoji: string; color: string }> = {
  instagram: { label: "Instagram", emoji: "📸", color: "bg-pink-500/10 text-pink-400" },
  facebook: { label: "Facebook", emoji: "📘", color: "bg-blue-500/10 text-blue-400" },
  tiktok: { label: "TikTok", emoji: "🎵", color: "bg-foreground/10 text-foreground" },
  twitter: { label: "X / Twitter", emoji: "🐦", color: "bg-sky-500/10 text-sky-400" },
  linkedin: { label: "LinkedIn", emoji: "💼", color: "bg-blue-600/10 text-blue-500" },
  youtube: { label: "YouTube", emoji: "🎬", color: "bg-red-500/10 text-red-400" },
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
                const config = PLATFORM_CONFIG[d.platform] || {
                  label: d.platform,
                  emoji: "🌐",
                  color: "bg-muted text-muted-foreground",
                };
                return (
                  <div
                    key={d.platform}
                    className="flex items-center gap-3 rounded-lg border border-border/30 bg-muted/30 p-3"
                  >
                    <span className="text-xl">{config.emoji}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{config.label}</p>
                      <p className="text-xs text-muted-foreground">
                        {d.followers.toLocaleString()} seguidores
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs">
                        {d.count} {d.count === 1 ? "cuenta" : "cuentas"}
                      </Badge>
                      {d.connected > 0 && (
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
