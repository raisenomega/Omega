import { Link } from "react-router-dom";

// Fase 1 · placeholder de la landing pública de OMEGA (cañería · SIN 3D · SIN deps nuevas).
// Existe para probar la ruta pública; el Hero real (3D, secciones, precios, formulario) llega en
// F3. Semántica limpia (un solo <h1>) = base SEO de F4. Estética oscura + dorado OMEGA (#EEA62B).
export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#0d0f14] flex flex-col items-center justify-center px-6 text-center">
      <div className="max-w-2xl space-y-6">
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-display font-bold tracking-tight text-white">
          Tu marketing digital, en <span className="text-[#EEA62B]">30 segundos</span>
        </h1>
        <p className="text-base sm:text-lg leading-relaxed text-white/70">
          Deja de saltar entre Meta, Google y cinco apps más. OMEGA lee todo y te dice qué
          publicar esta semana — en un lenguaje que entiendes.
        </p>
        <div className="flex flex-col items-center gap-3 pt-2">
          <Link
            to="/auth"
            className="inline-flex items-center justify-center rounded-full bg-[#EEA62B] px-8 py-3 text-base font-semibold text-black transition-transform hover:scale-105"
          >
            Empieza gratis 7 días
          </Link>
          <Link
            to="/auth"
            className="text-sm text-white/50 underline underline-offset-4 transition-colors hover:text-white/80"
          >
            Iniciar sesión
          </Link>
        </div>
      </div>
    </main>
  );
}
