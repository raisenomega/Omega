import { Building2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

// Switcher V1: estado de "sin negocio activo" para páginas contextuales. El CTA apunta al switcher
// del header (no abre nada directo · la selección vive en el header del sidebar).
export function EmptyState({ feature }: { feature: string }) {
  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardContent className="flex flex-col items-center justify-center py-16 text-center">
        <Building2 className="h-12 w-12 text-muted-foreground/30 mb-4" />
        <h3 className="text-lg font-medium mb-1">Sin negocio activo</h3>
        <p className="text-sm text-muted-foreground max-w-xs">
          Activá un negocio en el switcher del header para ver {feature}.
        </p>
      </CardContent>
    </Card>
  );
}
