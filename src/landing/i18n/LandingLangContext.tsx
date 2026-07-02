import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import { LANDING_STRINGS, type LandingLang, type LandingStrings } from "./landing-strings";

// Provider scoped SOLO a la landing (envuelve LandingPage · no toca el resto de OMEGA).
interface LandingLangCtx { lang: LandingLang; toggle: () => void; t: LandingStrings; }
const Ctx = createContext<LandingLangCtx | null>(null);

export function LandingLangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<LandingLang>("es");
  const toggle = useCallback(() => setLang((p) => (p === "es" ? "en" : "es")), []);
  return <Ctx.Provider value={{ lang, toggle, t: LANDING_STRINGS[lang] }}>{children}</Ctx.Provider>;
}

export function useLandingLang(): LandingLangCtx {
  const c = useContext(Ctx);
  if (!c) throw new Error("useLandingLang must be used within LandingLangProvider");
  return c;
}
