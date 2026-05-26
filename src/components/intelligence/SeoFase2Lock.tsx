import { Lock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

export function SeoFase2Lock() {
  return (
    <Card className="border-border/50 bg-card/40 opacity-70">
      <CardContent className="flex items-start gap-3 py-5">
        <Lock className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground/60" />
        <div className="space-y-1">
          <p className="text-sm font-medium text-muted-foreground">
            Posición en Google por keyword · Clicks e impresiones
          </p>
          <p className="text-xs text-muted-foreground/70 font-body">
            Requiere Google Search Console · Próximamente
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
