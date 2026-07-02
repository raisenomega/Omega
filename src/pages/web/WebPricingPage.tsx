import { Navigate } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";
import { useSuperOwner } from "@/hooks/useSuperOwner";
import { PricingTiersManager } from "@/components/web/PricingTiersManager";
import { PricingAddonsManager } from "@/components/web/PricingAddonsManager";

// Sitio Web · Precios · owner-only (is_super_owner · misma puerta in-page que las demás páginas web).
// Dos gestores apilados: Planes (tiers) + Add-ons. Cero campos Stripe (el checkout va aparte).
export default function WebPricingPage() {
  const { isSuperOwner, loading } = useSuperOwner();

  if (loading) return <Skeleton className="h-96 w-full" />;
  if (!isSuperOwner) return <Navigate to="/dashboard" replace />;

  return (
    <div className="mx-auto max-w-3xl space-y-12">
      <div>
        <h1 className="mb-1 font-display text-2xl font-bold text-foreground">Precios</h1>
        <p className="text-sm text-muted-foreground">Planes y add-ons de la sección Precios de la landing.</p>
      </div>
      <PricingTiersManager />
      <PricingAddonsManager />
    </div>
  );
}
