// Modelo de agente para la sección "Agentes IA" de AddOnsPage. 1 card por agente ·
// los tiers (Esencial/Pro) viven en el modal. Reusa los packs existentes como tiers
// (single source · cero re-tipeo de bullets). Frontend-only · sin Stripe aún.
// Mapeo persona→agente confirmado por owner: Rex/Rafa/Maya · Aria/Atlas/Luna reservadas.
import { PUBLISHER_PACKS } from "./_publisher_packs_data";
import { CREATIVE_PACKS } from "./_creative_packs_data";
import { TRENDS_PACK } from "./_trends_pack_data";

export interface AgentTier {
  label: string;
  code: string;          // DEBT-091 · agent_addon_code para el checkout (publisher_esencial, etc.)
  price: string;
  bullets: readonly string[];
  idealFor: string;
}

export interface Agent {
  id: string;
  persona: string;
  role: string;
  image: string;
  tagline: string;
  description: string;
  tiers: readonly AgentTier[];
}

const TIER_LABELS = ["Esencial", "Pro"] as const;

type PackLike = { readonly code: string; readonly price: string; readonly bullets: readonly string[]; readonly idealFor: string };

const toTiers = (packs: readonly PackLike[]): AgentTier[] =>
  packs.map((p, i) => ({
    label: TIER_LABELS[i] ?? `Tier ${i + 1}`,
    code: p.code,
    price: p.price,
    bullets: p.bullets,
    idealFor: p.idealFor,
  }));

export const AGENTS: readonly Agent[] = [
  {
    id: "publicador",
    persona: "Rex",
    role: "Agente Publicador",
    image: "/Agentes/Rex.jpg",
    tagline: "Publica automáticamente los posts que ya aprobaste, a su hora",
    description:
      "REX publica automáticamente los posts que ya aprobaste, a su hora programada. Tú apruebas, REX ejecuta. Próximamente: planificación semanal, mejor horario y reportes.",
    tiers: toTiers(PUBLISHER_PACKS),
  },
  {
    id: "creativo",
    persona: "Rafa",
    role: "Agente Creativo",
    image: "/Agentes/Rafa.jpg",
    tagline: "Crea contenido con IA y tu voz de marca",
    description:
      "Rafa es tu creador de contenido con IA. Genera captions, imágenes y videos con tu voz de marca aplicada, y aprende de cada aprobación para mejorar semana a semana.",
    tiers: toTiers(CREATIVE_PACKS),
  },
  {
    id: "tendencias",
    persona: "Maya",
    role: "Agente de Tendencias",
    image: "/Agentes/Maya.jpg",
    tagline: "Al día con tu mercado y tu competencia",
    description:
      "Maya mantiene a tu marca un paso adelante. Detecta tendencias de tu industria en tiempo real, monitorea a tu competencia y alimenta a ARIA con el contexto antes de cada generación.",
    tiers: [
      { label: "Plan único", code: TRENDS_PACK.code, price: TRENDS_PACK.price, bullets: TRENDS_PACK.bullets, idealFor: TRENDS_PACK.idealFor },
    ],
  },
] as const;
