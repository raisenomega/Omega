// Gate reusable de feature PRO · se muestra cuando !hasPro (acceso por URL directa).
// Espejo de IntelligencePlanGate pero parametrizado por feature. Frontend-only.
import { Lock, Loader2, ArrowUpRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useUpgradePlan } from "@/hooks/useUpgradePlan";

export function ProGateLoading() {
  return (
    <div className="container mx-auto max-w-5xl px-4 py-6">
      <Card className="border-border/50 bg-card/80">
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    </div>
  );
}

interface Props {
  feature: string;
  description?: string;
  clientId: string | null;
}

export function ProFeatureGate({ feature, description, clientId }: Props) {
  const upgrade = useUpgradePlan();
  return (
    <div className="container mx-auto max-w-5xl px-4 py-6">
      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardContent className="flex flex-col items-center justify-center py-16 gap-4 text-center">
          <Lock className="h-10 w-10 text-muted-foreground/40" />
          <p className="text-base font-medium text-foreground">
            {feature} está disponible en el plan PRO
          </p>
          {description && <p className="text-sm text-muted-foreground max-w-sm">{description}</p>}
          <Button
            disabled={upgrade.isPending || !clientId}
            onClick={() => clientId && upgrade.mutate({ clientId, targetPlan: "pro" })}
          >
            {upgrade.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <><ArrowUpRight className="h-4 w-4" />Subir a PRO</>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
