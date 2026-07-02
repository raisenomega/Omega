import { lazy, Suspense, Component, type ReactNode } from "react";
import { LandingLangProvider } from "@/landing/i18n/LandingLangContext";
import { useLandingSections } from "@/hooks/useLandingSections";
import { HeroSection } from "@/components/landing/HeroSection";
import { LandingHeader } from "@/components/landing/LandingHeader";
import { LandingFooter } from "@/components/landing/LandingFooter";

// Fase 3 · Rebanada 1 · landing pública OMEGA. El Canvas 3D va SIEMPRE lazy → su chunk
// (three/fiber/drei) solo lo carga la landing, nunca el bundle inicial de la app. Suspense
// fallback null + ErrorBoundary → si el 3D falla o no hay WebGL, el texto (z-10) renderiza igual.
// En esta rebanada SOLO el Hero tiene componente real (las demás secciones llegan en rebanadas siguientes).
const HeroScene = lazy(() =>
  import("@/components/landing/HeroScene").then((m) => ({ default: m.HeroScene })),
);

class SceneBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? null : this.props.children;
  }
}

function LandingContent() {
  const { isVisible } = useLandingSections();
  return (
    <>
      {/* Fondo 3D fijo (z-0) · el contenido va encima en z-10 */}
      <div className="fixed inset-0 z-0" style={{ background: "hsl(225 15% 5%)" }}>
        <Suspense fallback={null}>
          <SceneBoundary>
            <HeroScene />
          </SceneBoundary>
        </Suspense>
      </div>

      <div className="relative z-10">
        <LandingHeader />
        <main>{isVisible("hero") && <HeroSection />}</main>
        <LandingFooter />
      </div>
    </>
  );
}

export default function LandingPage() {
  return (
    <LandingLangProvider>
      <LandingContent />
    </LandingLangProvider>
  );
}
