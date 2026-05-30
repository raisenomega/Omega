import { createContext, useContext, useEffect, useState, ReactNode } from "react";

// ARIAContext · drawer visibility state · persiste isOpen en sessionStorage
// (sobrevive navegación entre rutas SPA · sesión completa hasta logout)
interface ARIAContextValue {
  isOpen: boolean;
  pendingMessage: string | null;   // mensaje a pre-cargar en el input al abrir (ej. "Pedir ajuste")
  openARIA: () => void;
  openARIAWith: (message: string) => void;
  clearPending: () => void;
  closeARIA: () => void;
  toggleARIA: () => void;
}

const ARIAContext = createContext<ARIAContextValue | undefined>(undefined);

const STORAGE_KEY = "aria_drawer_open";

export function ARIAProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState<boolean>(() => {
    if (typeof window === "undefined") return false;
    return sessionStorage.getItem(STORAGE_KEY) === "true";
  });

  useEffect(() => {
    sessionStorage.setItem(STORAGE_KEY, isOpen ? "true" : "false");
  }, [isOpen]);

  const [pendingMessage, setPendingMessage] = useState<string | null>(null);

  const openARIA = () => setIsOpen(true);
  const openARIAWith = (message: string) => { setPendingMessage(message); setIsOpen(true); };
  const clearPending = () => setPendingMessage(null);
  const closeARIA = () => setIsOpen(false);
  const toggleARIA = () => setIsOpen((p) => !p);

  return (
    <ARIAContext.Provider
      value={{ isOpen, pendingMessage, openARIA, openARIAWith, clearPending, closeARIA, toggleARIA }}
    >
      {children}
    </ARIAContext.Provider>
  );
}

export function useARIA() {
  const ctx = useContext(ARIAContext);
  if (!ctx) throw new Error("useARIA debe usarse dentro de <ARIAProvider>");
  return ctx;
}
