import { createContext, useCallback, useContext, useEffect, useMemo, ReactNode } from "react";
import { useSearchParams } from "react-router-dom";
import { useMyClients } from "@/hooks/useMyClients";

interface ActiveBusinessValue {
  activeBusinessId: string | null;
  setActiveBusiness: (id: string | null) => void;
  isReady: boolean;
}

const ActiveBusinessContext = createContext<ActiveBusinessValue | undefined>(undefined);

// Negocio activo global, sincronizado con ?business={id} (la URL es la fuente de verdad · refresh y
// compartir-link conservan la selección). Auto-selecciona si N=1 (backward-compat cliente@omega →
// Zafacones). N>=2 lo elige el usuario en el switcher. `isReady` evita el flash de empty-state durante
// la carga de useMyClients y la auto-selección. Cero backend · solo lectura del estado actual.
export function ActiveBusinessProvider({ children }: { children: ReactNode }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const { data: clients, isLoading } = useMyClients();
  const urlId = searchParams.get("business");

  const setActiveBusiness = useCallback((id: string | null) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (id) next.set("business", id);
      else next.delete("business");
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  // N=1 sin selección en URL → auto-seleccionar el único negocio (no flashea empty-state).
  const pendingAutoSelect = !isLoading && !urlId && clients?.length === 1;

  useEffect(() => {
    if (pendingAutoSelect && clients) setActiveBusiness(clients[0].id);
  }, [pendingAutoSelect, clients, setActiveBusiness]);

  const value = useMemo<ActiveBusinessValue>(() => ({
    activeBusinessId: urlId,
    setActiveBusiness,
    isReady: !isLoading && !pendingAutoSelect,
  }), [urlId, setActiveBusiness, isLoading, pendingAutoSelect]);

  return <ActiveBusinessContext.Provider value={value}>{children}</ActiveBusinessContext.Provider>;
}

export function useActiveBusiness(): ActiveBusinessValue {
  const ctx = useContext(ActiveBusinessContext);
  if (!ctx) throw new Error("useActiveBusiness must be used within ActiveBusinessProvider");
  return ctx;
}
