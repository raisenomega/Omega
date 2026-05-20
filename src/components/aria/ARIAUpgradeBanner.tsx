import { ArrowUpRight } from "lucide-react";
import { Button } from "@/components/ui/button";

// Banner upgrade ARIA Premium · Q1=A · botón disabled hasta que existan
// productos Stripe ARIA Premium (product_aria_premium_client $12/mes ·
// product_aria_premium_reseller $25/mes · pending Fase 2 · DEBT-037)

interface ARIAUpgradeBannerProps {
  currentLevel: number;
}

export function ARIAUpgradeBanner({ currentLevel }: ARIAUpgradeBannerProps) {
  if (currentLevel === 1 || currentLevel >= 4) return null;

  const targetLevel = currentLevel + 1;

  return (
    <div className="border-t border-border bg-muted/30 px-3 py-2 flex items-center justify-between gap-2">
      <span className="text-xs text-muted-foreground">
        Actualizar a ARIA {targetLevel}.0 — $12/mes
      </span>
      <Button
        size="sm"
        variant="outline"
        disabled
        className="h-7 gap-1 text-xs"
        title="ARIA Premium próximamente · pending DEBT-037"
      >
        <ArrowUpRight className="h-3 w-3" />
        Próximamente
      </Button>
    </div>
  );
}
