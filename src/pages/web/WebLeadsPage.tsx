import { Navigate } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";
import { useSuperOwner } from "@/hooks/useSuperOwner";
import { LeadsInbox } from "@/components/web/LeadsInbox";

// Sitio Web · Leads · owner-only (is_super_owner · misma puerta que las demás páginas web).
// El backend (GET /platform/leads) también exige super_owner; este gate solo evita render a no-owners.
export default function WebLeadsPage() {
  const { isSuperOwner, loading } = useSuperOwner();

  if (loading) return <Skeleton className="h-96 w-full" />;
  if (!isSuperOwner) return <Navigate to="/dashboard" replace />;

  return <LeadsInbox />;
}
