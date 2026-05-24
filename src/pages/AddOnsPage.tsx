import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { Package, Video } from "lucide-react";
import { VideoPackCard } from "@/components/addons/VideoPackCard";
import { VIDEO_PACKS } from "@/components/addons/_video_packs_data";
import { useVideoPackCheckout } from "@/hooks/useVideoPackCheckout";

interface NavState {
  scrollTo?: string;
}

export default function AddOnsPage() {
  const location = useLocation();
  const videoRef = useRef<HTMLElement>(null);
  const checkout = useVideoPackCheckout();  // DEBT-VID-001

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

      {/* Sprint 4+: section Agentes Especializados · section ARIA Premium · etc */}
    </div>
  );
}
