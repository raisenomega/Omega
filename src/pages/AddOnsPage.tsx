import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { Package, Video, Send, Wand2, TrendingUp } from "lucide-react";
import { VideoPackCard } from "@/components/addons/VideoPackCard";
import { VIDEO_PACKS } from "@/components/addons/_video_packs_data";
import { PUBLISHER_PACKS } from "@/components/addons/_publisher_packs_data";
import { CREATIVE_PACKS } from "@/components/addons/_creative_packs_data";
import { TRENDS_PACK } from "@/components/addons/_trends_pack_data";
import { useVideoPackCheckout } from "@/hooks/useVideoPackCheckout";
import { useToast } from "@/hooks/use-toast";

interface NavState {
  scrollTo?: string;
}

export default function AddOnsPage() {
  const location = useLocation();
  const videoRef = useRef<HTMLElement>(null);
  const checkout = useVideoPackCheckout();  // DEBT-VID-001
  const { toast } = useToast();

  // Add-ons sin Stripe product aún → toast honesto (P1 · no cobra por lo no construido).
  const comingSoon = () =>
    toast({ title: "Próximamente", description: "Disponible pronto · contáctanos para early access." });

  useEffect(() => {
    const state = location.state as NavState | null;
    if (state?.scrollTo === "video-packs") {
      videoRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [location.state]);

  return (
    <div className="space-y-8">
      <header className="flex items-center gap-2">
        <Package className="h-5 w-5 text-amber-500" />
        <div>
          <h1 className="text-2xl font-semibold">Add-Ons</h1>
          <p className="text-sm text-muted-foreground">Potenciá tu plan con paquetes especializados.</p>
        </div>
      </header>

      <section ref={videoRef} id="video-packs" className="space-y-3">
        <div className="flex items-center gap-2">
          <Video className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Video Packs</h2>
        </div>
        <p className="text-xs text-muted-foreground">Generación con Veo 3.1 · audio nativo · ARIA + Brand DNA aplicado</p>
        <div className="grid gap-4 md:grid-cols-3">
          {VIDEO_PACKS.map((p) => (
            <VideoPackCard
              key={p.code}
              name={p.name}
              price={p.price}
              bullets={p.bullets}
              idealFor={p.idealFor}
              onActivate={() => checkout.mutate({ video_pack_code: p.code })}
              isPending={checkout.isPending}
            />
          ))}
        </div>
      </section>

      <section id="agente-publicador" className="space-y-3">
        <div className="flex items-center gap-2">
          <Send className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Agente Publicador</h2>
        </div>
        <p className="text-xs text-muted-foreground">Tu agente que gestiona y recuerda tu calendario de publicación</p>
        <div className="grid gap-4 md:grid-cols-2">
          {PUBLISHER_PACKS.map((p) => (
            <VideoPackCard
              key={p.code}
              name={p.name}
              price={p.price}
              bullets={p.bullets}
              idealFor={p.idealFor}
              ctaLabel="Activar"
              onActivate={() =>
                toast({
                  title: "Próximamente",
                  description: "El Agente Publicador estará disponible pronto · contáctanos para early access.",
                })
              }
            />
          ))}
        </div>
      </section>

      <section id="agente-creativo" className="space-y-3">
        <div className="flex items-center gap-2">
          <Wand2 className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Agente Creativo</h2>
        </div>
        <p className="text-xs text-muted-foreground">Tu creador de contenido con IA y voz de marca aplicada</p>
        <div className="grid gap-4 md:grid-cols-2">
          {CREATIVE_PACKS.map((p) => (
            <VideoPackCard
              key={p.code}
              name={p.name}
              price={p.price}
              bullets={p.bullets}
              idealFor={p.idealFor}
              ctaLabel="Activar"
              onActivate={comingSoon}
            />
          ))}
        </div>
      </section>

      <section id="agente-tendencias" className="space-y-3">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Agente de Tendencias</h2>
        </div>
        <p className="text-xs text-muted-foreground">Siempre al día con tu mercado y tu competencia</p>
        <div className="grid gap-4 md:grid-cols-2">
          <VideoPackCard
            name={TRENDS_PACK.name}
            price={TRENDS_PACK.price}
            bullets={TRENDS_PACK.bullets}
            idealFor={TRENDS_PACK.idealFor}
            ctaLabel="Activar"
            onActivate={comingSoon}
          />
        </div>
      </section>

      {/* Sprint 4+: section ARIA Premium · etc */}
    </div>
  );
}
