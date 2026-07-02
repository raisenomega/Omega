import { Navigate } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";
import { useSuperOwner } from "@/hooks/useSuperOwner";
import { ProcessManager } from "@/components/web/ProcessManager";

// Sitio Web · Proceso · owner-only (is_super_owner · misma puerta in-page que Secciones/Servicios).
// La RLS super_owner de landing_process_steps es la defensa real; este gate solo evita render a no-owners.
export default function WebProcessPage() {
  const { isSuperOwner, loading } = useSuperOwner();

  if (loading) return <Skeleton className="h-96 w-full" />;
  if (!isSuperOwner) return <Navigate to="/dashboard" replace />;

  return <ProcessManager />;
}
