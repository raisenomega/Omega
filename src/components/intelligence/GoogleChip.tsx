import { LineChart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

const FEATURES = [
  "Visitas desde redes",
  "Keywords que traen tráfico",
  "Páginas más visitadas",
  "ROI real de tus posts",
];

const PREVIEW = [
  { label: "Visitas / redes", hint: "—" },
  { label: "Top keyword", hint: "—" },
  { label: "ROI estimado", hint: "—" },
];

export function GoogleChip() {
  return (
    <Card className="border-border/50 bg-card/60 backdrop-blur-sm">
      <CardContent className="flex flex-col items-center gap-5 py-10">
        <div className="flex flex-col items-center gap-3 text-center">
          <LineChart className="h-12 w-12 text-amber-500" />
          <Badge variant="outline" className="border-amber-500/40 text-amber-500">
            Fase 2 · Próximamente
          </Badge>
          <p className="text-base font-medium text-foreground">Conecta Google para ver:</p>
          <ul className="space-y-1 text-sm text-muted-foreground font-body">
            {FEATURES.map((f) => (
              <li key={f}>· {f}</li>
            ))}
          </ul>
        </div>

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              {/* span: tooltip funciona aunque el botón esté disabled */}
              <span tabIndex={0}>
                <Button disabled className="bg-amber-500/90 text-black hover:bg-amber-500">
                  Conectar Google Analytics
                </Button>
              </span>
            </TooltipTrigger>
            <TooltipContent>Próximamente</TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <div className="w-full space-y-2">
          <p className="text-center text-xs uppercase tracking-wide text-muted-foreground/60">
            Vista previa · datos de ejemplo (aún no conectado)
          </p>
          <div className="grid grid-cols-3 gap-2 opacity-50">
            {PREVIEW.map((p) => (
              <div key={p.label} className="rounded-md border border-dashed border-border/60 bg-muted/20 px-3 py-4 text-center">
                <p className="text-[10px] uppercase text-muted-foreground/70">{p.label}</p>
                <p className="mt-1 text-lg font-semibold text-muted-foreground/50">{p.hint}</p>
                <Badge variant="outline" className="mt-1 border-border/40 text-[9px] text-muted-foreground/60">
                  vista previa
                </Badge>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
