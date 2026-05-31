import { useState, useCallback, useEffect } from "react";
import { useSearchParams } from "react-router-dom";

// Estado del modal del wizard de negocio (Switcher V1 · A2). Dueño de isOpen + editingClientId
// para que el switcher del header pueda abrir "Nuevo Negocio" vía ?new=1 desde cualquier página.
// UI state puro (no domain). El form.reset() del modo nuevo lo hace Clients.tsx por useEffect
// (DEBT-WIZARD-RESET-DECLARATIVE).
export function useBusinessWizardModal() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [isOpen, setIsOpen] = useState(false);
  const [editingClientId, setEditingClientId] = useState<string | null>(null);

  const openNew = useCallback(() => { setEditingClientId(null); setIsOpen(true); }, []);
  const openEdit = useCallback((id: string) => { setEditingClientId(id); setIsOpen(true); }, []);
  const close = useCallback(() => { setIsOpen(false); setEditingClientId(null); }, []);

  // ?new=1 (lo setea el switcher) → abre el modal de creación + limpia el param (replace).
  useEffect(() => {
    if (searchParams.get("new") !== "1") return;
    openNew();
    const next = new URLSearchParams(searchParams);
    next.delete("new");
    setSearchParams(next, { replace: true });
  }, [searchParams, setSearchParams, openNew]);

  return { isOpen, editingClientId, openNew, openEdit, close };
}
