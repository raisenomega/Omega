import { createContext, useCallback, useContext, useEffect, useMemo, ReactNode } from "react";
import { useSearchParams } from "react-router-dom";
import { useMyClients } from "@/hooks/useMyClients";

interface ActiveBusinessValue {
  activeBusinessId: string | null;
  setActiveBusiness: (id: string | null) => void;
  isReady: boolean;
}

const ActiveBusinessContext = createContext<ActiveBusinessValue | undefined>(undefined);
const LS_KEY = "omega.activeBusinessId";

const readStored = (): string | null => {
  try { return localStorage.getItem(LS_KEY); } catch { return null; }
};
const writeStored = (id: string | null) => {
  try { if (id) localStorage.setItem(LS_KEY, id); else localStorage.removeItem(LS_KEY); } catch { /* sin storage */ }
};

// Negocio activo global. Persistido en localStorage (sobrevive a la navegación interna, que con N>=2
// perdía el ?business y apagaba las páginas) y espejado en ?business={id} para refresh/compartir-link.
// id efectivo = URL ?? localStorage, validado contra la cartera real (tras "borré todo y recreé", un id
// viejo queda stale y se limpia). N=1 auto-selecciona; N>=2 lo elige el usuario y queda fijo. `isReady`
// evita el flash de empty-state durante la carga. Cero backend · solo lectura del estado actual.
export function ActiveBusinessProvider({ children }: { children: ReactNode }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const { data: clients, isLoading } = useMyClients();
  const urlId = searchParams.get("business");
  const candidateId = urlId ?? readStored();
  const validId = clients?.some((c) => c.id === candidateId) ? candidateId : null;

  const setActiveBusiness = useCallback((id: string | null) => {
    writeStored(id);
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (id) next.set("business", id);
      else next.delete("business");
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  // N=1 sin selección → auto-seleccionar. Restaurar URL tras navegación. Limpiar id stale.
  const pendingAutoSelect = !isLoading && !validId && clients?.length === 1;

  useEffect(() => {
    if (pendingAutoSelect && clients) { setActiveBusiness(clients[0].id); return; }
    if (!validId) { if (!isLoading && candidateId) writeStored(null); return; }
    writeStored(validId);
    if (validId !== urlId) setActiveBusiness(validId);
  }, [pendingAutoSelect, clients, validId, urlId, candidateId, isLoading, setActiveBusiness]);

  const value = useMemo<ActiveBusinessValue>(() => ({
    activeBusinessId: validId,
    setActiveBusiness,
    isReady: !isLoading && !pendingAutoSelect,
  }), [validId, setActiveBusiness, isLoading, pendingAutoSelect]);

  return <ActiveBusinessContext.Provider value={value}>{children}</ActiveBusinessContext.Provider>;
}

export function useActiveBusiness(): ActiveBusinessValue {
  const ctx = useContext(ActiveBusinessContext);
  if (!ctx) throw new Error("useActiveBusiness must be used within ActiveBusinessProvider");
  return ctx;
}
