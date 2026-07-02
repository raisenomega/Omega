import { Navigate } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";
import { useSuperOwner } from "@/hooks/useSuperOwner";
import { LandingSectionsManager } from "@/components/web/LandingSectionsManager";

// Sitio Web · Secciones · owner-only (is_super_owner · misma puerta in-page que NOVA/Security Dev).
// La RLS super_owner de landing_sections es la defensa real; este gate solo evita render/UX a no-owners.
export default function WebSectionsPage() {
  const { isSuperOwner, loading } = useSuperOwner();

  if (loading) return <Skeleton className="h-96 w-full" />;
  if (!isSuperOwner) return <Navigate to="/dashboard" replace />;

  return <LandingSectionsManager />;
}
