import { Lock, Loader2, ArrowUpRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useUpgradePlan } from "@/hooks/useUpgradePlan";

interface Props { clientId: string | null; }

export function IntelligenceLoading() {
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

export function IntelligencePlanGate({ clientId }: Props) {
  const upgrade = useUpgradePlan();
  return (
    <div className="container mx-auto max-w-5xl px-4 py-6">
      <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
        <CardContent className="flex flex-col items-center justify-center py-16 gap-4 text-center">
          <Lock className="h-10 w-10 text-muted-foreground/40" />
          <p className="text-base font-medium text-foreground">
            El Centro de Inteligencia está disponible en el plan PRO
          </p>
          <p className="text-sm text-muted-foreground max-w-sm">
            Accedé a análisis SEO, GEO, AEO, Meta y Google de tu presencia digital.
          </p>
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
