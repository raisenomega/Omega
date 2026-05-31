import { useState, useCallback, useEffect } from "react";
import { useSearchParams } from "react-router-dom";

// Estado del modal del wizard de negocio (Switcher V1 · A2). 2 fases en creación: intro educativo → wizard.
// Dueño de introOpen + isOpen + editingClientId para que el switcher abra "Nuevo Negocio" vía ?new=1 desde
// cualquier página. UI state puro (no domain). Editar va directo al wizard (sin intro). El form.reset() del
// modo nuevo lo hace Clients.tsx por useEffect (DEBT-WIZARD-RESET-DECLARATIVE).
export function useBusinessWizardModal() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [introOpen, setIntroOpen] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [editingClientId, setEditingClientId] = useState<string | null>(null);

  const openNew = useCallback(() => { setEditingClientId(null); setIntroOpen(true); }, []);
  const openEdit = useCallback((id: string) => { setEditingClientId(id); setIsOpen(true); }, []);
  const acceptIntro = useCallback(() => { setIntroOpen(false); setIsOpen(true); }, []);
  const cancelIntro = useCallback(() => { setIntroOpen(false); setEditingClientId(null); }, []);
  const close = useCallback(() => { setIsOpen(false); setEditingClientId(null); }, []);

  // ?new=1 (lo setea el switcher) → abre el intro de creación + limpia el param (replace).
  useEffect(() => {
    if (searchParams.get("new") !== "1") return;
    openNew();
    const next = new URLSearchParams(searchParams);
    next.delete("new");
    setSearchParams(next, { replace: true });
  }, [searchParams, setSearchParams, openNew]);

  return { introOpen, isOpen, editingClientId, openNew, openEdit, acceptIntro, cancelIntro, close };
}
