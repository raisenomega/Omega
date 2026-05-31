import { useNavigate } from "react-router-dom";
import { ChevronDown, Plus, Building2, X, Check } from "lucide-react";
import {
  DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { useMyClients } from "@/hooks/useMyClients";
import { useMyPlanStatus } from "@/hooks/useMyPlanStatus";
import { useSuperOwner } from "@/hooks/useSuperOwner";
import { useActiveBusiness } from "@/contexts/ActiveBusinessContext";

// Switcher de negocio activo (Switcher V1). 3 casos según rol:
// · super_owner (cuenta admin) → "Superadmin", sin switcher (no opera negocios).
// · cliente puro (no reseller · N=1) → informativo: punto verde + nombre, sin dropdown.
// · reseller/owner → dropdown funcional: cartera + "Nuevo Negocio" + "Desactivar".
// Solo lectura de estado (useMyClients + useActiveBusiness) · cero backend.
const BOX = "flex items-center gap-2 rounded-md border border-sidebar-border/50 bg-sidebar-accent/30 px-2 py-1.5 text-xs w-full group-data-[collapsible=icon]:hidden";

export function BusinessSwitcher() {
  const navigate = useNavigate();
  const { isSuperOwner } = useSuperOwner();
  const { isOwner } = useMyPlanStatus();
  const { data: clients } = useMyClients();
  const { activeBusinessId, setActiveBusiness } = useActiveBusiness();

  if (isSuperOwner) {
    return <div className={BOX}><span className="font-semibold text-amber-500">Superadmin</span></div>;
  }

  const list = clients ?? [];
  const active = list.find((c) => c.id === activeBusinessId);

  if (!isOwner) {
    return (
      <div className={BOX}>
        <span className="h-2 w-2 shrink-0 rounded-full bg-green-500" />
        <span className="truncate font-medium">{active?.name ?? list[0]?.name ?? "Mi negocio"}</span>
      </div>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className={BOX}>
        {active ? (
          <>
            <span className="h-2 w-2 shrink-0 rounded-full bg-green-500" />
            <span className="truncate font-medium flex-1 text-left">{active.name}</span>
          </>
        ) : (
          <span className="flex-1 text-left text-muted-foreground">Activá un negocio</span>
        )}
        <ChevronDown className="h-3.5 w-3.5 shrink-0 opacity-60" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-56">
        {list.map((c) => (
          <DropdownMenuItem key={c.id} onClick={() => setActiveBusiness(c.id)} className="gap-2">
            <Building2 className="h-3.5 w-3.5" />
            <span className="truncate flex-1">{c.name}</span>
            {c.id === activeBusinessId && <Check className="h-3.5 w-3.5" />}
          </DropdownMenuItem>
        ))}
        {list.length > 0 && <DropdownMenuSeparator />}
        <DropdownMenuItem onClick={() => navigate("/clients?new=1")} className="gap-2">
          <Plus className="h-3.5 w-3.5" /> Nuevo Negocio
        </DropdownMenuItem>
        {activeBusinessId && (
          <DropdownMenuItem onClick={() => setActiveBusiness(null)} className="gap-2 text-muted-foreground">
            <X className="h-3.5 w-3.5" /> Desactivar
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
