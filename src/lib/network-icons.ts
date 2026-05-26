import { Camera, Square, Music2, Briefcase, Globe } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export interface NetworkIconConfig {
  icon: LucideIcon;
  label: string;
}

// Single source of truth: iconos Lucide para redes sociales, consistente con
// el sistema del sidebar (no emojis). Las 4 redes canónicas del modelo §3
// usan icono específico; el resto cae al fallback Globe.
const ICONS: Record<string, NetworkIconConfig> = {
  instagram: { icon: Camera, label: "Instagram" },
  facebook: { icon: Square, label: "Facebook" },
  tiktok: { icon: Music2, label: "TikTok" },
  linkedin: { icon: Briefcase, label: "LinkedIn" },
};

const FALLBACK: NetworkIconConfig = { icon: Globe, label: "Otra red" };

export function getNetworkIcon(platform: string): NetworkIconConfig {
  return ICONS[platform] ?? FALLBACK;
}

// Etiquetas display por plataforma (incluye redes sin icono específico).
export const PLATFORM_LABELS: Record<string, string> = {
  instagram: "Instagram",
  facebook: "Facebook",
  tiktok: "TikTok",
  twitter: "X/Twitter",
  linkedin: "LinkedIn",
  youtube: "YouTube",
};
