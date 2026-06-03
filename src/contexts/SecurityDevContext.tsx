import { createContext, useContext, useState, ReactNode } from "react";

// Estado compartido del panel /security-dev: tab activo (para navegar Fix→Dev Chat)
// + prompt de fix pendiente que Dev Chat muestra (placeholder hasta Sprint 8 · DEBT-106).
export type SecurityDevTab = "sentinel" | "guardian" | "hermes" | "chat" | "terminal";

interface SecurityDevCtx {
  activeTab: SecurityDevTab;
  setActiveTab: (t: SecurityDevTab) => void;
  pendingFixPrompt: string | null;
  setPendingFixPrompt: (p: string | null) => void;
}

const Ctx = createContext<SecurityDevCtx | null>(null);

export function SecurityDevProvider({ children }: { children: ReactNode }) {
  const [activeTab, setActiveTab] = useState<SecurityDevTab>("sentinel");
  const [pendingFixPrompt, setPendingFixPrompt] = useState<string | null>(null);
  return (
    <Ctx.Provider value={{ activeTab, setActiveTab, pendingFixPrompt, setPendingFixPrompt }}>
      {children}
    </Ctx.Provider>
  );
}

export function useSecurityDev(): SecurityDevCtx {
  const c = useContext(Ctx);
  if (!c) throw new Error("useSecurityDev must be used within SecurityDevProvider");
  return c;
}
