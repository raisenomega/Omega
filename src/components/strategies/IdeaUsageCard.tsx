import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";
import { PLATFORM_LABELS } from "@/lib/onboarding-constants";
import type { UsedIdea } from "@/hooks/useUsedIdeas";

// Fase B.2 · tarjeta de una IDEA usada (no una estrategia): red + texto + "De: {título}" + Re-usar.
// SIN tipo de post (Reel/etc · no existe el dato · decisión del owner). Fallback honesto si falta el
// título (estrategia eliminada). Re-usar navega a Content Lab con el brief de ESA idea (registro = B.3).
export function IdeaUsageCard({ idea }: { idea: UsedIdea }) {
  const navigate = useNavigate();
  const red = idea.platform
    ? (PLATFORM_LABELS[idea.platform as keyof typeof PLATFORM_LABELS] ?? idea.platform)
    : "Sin red";
  const origen = idea.strategies?.titulo ?? "(estrategia eliminada)";

  const reusar = () =>
    navigate("/content-lab", { state: { brief: idea.brief, ...(idea.platform ? { platform: idea.platform } : {}) } });

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardContent className="p-3 space-y-2">
        <Badge variant="secondary" className="text-[10px]">{red}</Badge>
        {idea.brief && <p className="text-sm line-clamp-4">{idea.brief}</p>}
        <p className="text-[10px] text-muted-foreground line-clamp-1">De: {origen}</p>
        <Button size="sm" className="gap-1 h-8 w-full" onClick={reusar}>
          <Sparkles className="h-3.5 w-3.5" /> Re-usar
        </Button>
      </CardContent>
    </Card>
  );
}
