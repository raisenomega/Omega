import { Navigate } from "react-router-dom";
import { Skeleton } from "@/components/ui/skeleton";
import { useSuperOwner } from "@/hooks/useSuperOwner";
import { NovaChat } from "@/components/nova/NovaChat";

// NOVA · módulo owner-only (DEBT-IDOR-NOVA · backend exige require_superadmin).
// Gating idéntico a Security Dev: super_owner ve el chat · resto → /dashboard.
export default function Nova() {
  const { isSuperOwner, loading } = useSuperOwner();

  if (loading) return <Skeleton className="h-96 w-full" />;
  if (!isSuperOwner) return <Navigate to="/dashboard" replace />;

  return <NovaChat />;
}
