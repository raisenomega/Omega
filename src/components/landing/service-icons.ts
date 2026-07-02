// Fuente única de íconos válidos para servicios (nombre lucide en la columna `icon`).
// Lo consumen ServiceCard (render de la landing) y el editor de Servicios (dropdown · Checkpoint C).
// Los 4 sembrados usan Sparkles/CalendarDays/BarChart3/Bot; el resto amplía el set del owner.
import {
  Sparkles,
  CalendarDays,
  BarChart3,
  Bot,
  Target,
  Search,
  Palette,
  Zap,
  Rocket,
  MessageSquare,
  TrendingUp,
  Users,
  Globe,
  Image,
  Video,
  type LucideIcon,
} from "lucide-react";

export const SERVICE_ICONS: Record<string, LucideIcon> = {
  Sparkles,
  CalendarDays,
  BarChart3,
  Bot,
  Target,
  Search,
  Palette,
  Zap,
  Rocket,
  MessageSquare,
  TrendingUp,
  Users,
  Globe,
  Image,
  Video,
};

export const SERVICE_ICON_NAMES = Object.keys(SERVICE_ICONS);

export const serviceIcon = (name: string): LucideIcon => SERVICE_ICONS[name] ?? Target;
