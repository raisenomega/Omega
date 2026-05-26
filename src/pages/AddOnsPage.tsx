import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { Package, Video, Bot } from "lucide-react";
import { VideoPackCard } from "@/components/addons/VideoPackCard";
import { SectionDivider } from "@/components/addons/SectionDivider";
import { PlansSection } from "@/components/addons/PlansSection";
import { AgentCard } from "@/components/addons/AgentCard";
import { AgentDetailModal } from "@/components/addons/AgentDetailModal";
import { VIDEO_PACKS } from "@/components/addons/_video_packs_data";
import { AGENTS, type Agent } from "@/components/addons/_agents_data";
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
  const [openAgent, setOpenAgent] = useState<Agent | null>(null);

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

      <PlansSection />

      <SectionDivider />

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

      <SectionDivider />

      <section id="agentes" className="space-y-3">
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Agentes IA</h2>
        </div>
        <p className="text-xs text-muted-foreground">Tu equipo de agentes especializados · activá los que tu marca necesita</p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {AGENTS.map((agent) => (
            <AgentCard key={agent.id} agent={agent} onOpen={() => setOpenAgent(agent)} />
          ))}
        </div>
      </section>

      <AgentDetailModal
        agent={openAgent}
        onClose={() => setOpenAgent(null)}
        onActivate={() => {
          setOpenAgent(null);
          comingSoon();
        }}
      />

      {/* Sprint 4+: section ARIA Premium · etc */}
    </div>
  );
}
