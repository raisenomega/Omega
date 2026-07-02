import { Navigate } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";
import { useSuperOwner } from "@/hooks/useSuperOwner";
import { ServicesManager } from "@/components/web/ServicesManager";

// Sitio Web · Servicios · owner-only (is_super_owner · misma puerta in-page que Secciones/NOVA).
// La RLS super_owner de landing_services es la defensa real; este gate solo evita render a no-owners.
export default function WebServicesPage() {
  const { isSuperOwner, loading } = useSuperOwner();

  if (loading) return <Skeleton className="h-96 w-full" />;
  if (!isSuperOwner) return <Navigate to="/dashboard" replace />;

  return <ServicesManager />;
}
