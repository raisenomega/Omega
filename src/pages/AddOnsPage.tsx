import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Package, Video, Bot, Sparkles, Coins } from "lucide-react";
import { VideoPackCard } from "@/components/addons/VideoPackCard";
import { SectionDivider } from "@/components/addons/SectionDivider";
import { PlansSection } from "@/components/addons/PlansSection";
import { AgentCard } from "@/components/addons/AgentCard";
import { AgentDetailModal } from "@/components/addons/AgentDetailModal";
import { VIDEO_PACKS } from "@/components/addons/_video_packs_data";
import { AGENTS, type Agent } from "@/components/addons/_agents_data";
import { useVideoPackCheckout } from "@/hooks/useVideoPackCheckout";
import { useAgentAddonCheckout } from "@/hooks/useAgentAddonCheckout";
import { useMyPlanStatus } from "@/hooks/useMyPlanStatus";
import { AriaLevelChips } from "@/components/clients/AriaLevelChips";
import { AriaUpgradeModal } from "@/components/clients/AriaUpgradeModal";
import { CreditPackModal } from "@/components/clients/CreditPackModal";

interface NavState {
  scrollTo?: string;
}

export default function AddOnsPage() {
  const location = useLocation();
  const videoRef = useRef<HTMLElement>(null);
  const agentesRef = useRef<HTMLElement>(null);
  const checkout = useVideoPackCheckout();  // DEBT-VID-001
  const agentCheckout = useAgentAddonCheckout();  // DEBT-091 · Stripe real (503 honesto si price no configurado)
  const [openAgent, setOpenAgent] = useState<Agent | null>(null);
  const { clientId } = useMyPlanStatus();
  const { data: ariaLevel = 1 } = useQuery({
    queryKey: ["client_aria_level", clientId],
    queryFn: async () => {
      const { data } = await supabase.from("clients").select("aria_level").eq("id", clientId!).maybeSingle();
      return data?.aria_level ?? 1;
    },
    enabled: !!clientId,
  });

  useEffect(() => {
    const state = location.state as NavState | null;
    if (state?.scrollTo === "video-packs") {
      videoRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    if (location.hash === "#agentes") {
      agentesRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [location.state, location.hash]);

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

      <section ref={agentesRef} id="agentes" className="space-y-3">
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

      <SectionDivider />

      <section id="aria" className="space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Mejora tu ARIA</h2>
        </div>
        <p className="text-xs text-muted-foreground">Tu asistente de marca · subí de nivel cuando lo necesites</p>
        <div className="flex flex-wrap items-center gap-3">
          <AriaLevelChips currentLevel={ariaLevel} />
          <AriaUpgradeModal currentLevel={ariaLevel} />
        </div>
      </section>

      <SectionDivider />

      <section id="creditos" className="space-y-3">
        <div className="flex items-center gap-2">
          <Coins className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-lg font-semibold">Añadir Créditos</h2>
        </div>
        <p className="text-xs text-muted-foreground">Amplía tu capacidad de generación · sin cambiar tu plan</p>
        <div className="max-w-xs">
          <CreditPackModal />
        </div>
      </section>

      <AgentDetailModal
        agent={openAgent}
        onClose={() => setOpenAgent(null)}
        onActivate={(code) => {
          setOpenAgent(null);
          agentCheckout.mutate({ agent_addon_code: code });
        }}
      />

      {/* Sprint 4+: section ARIA Premium · etc */}
    </div>
  );
}
