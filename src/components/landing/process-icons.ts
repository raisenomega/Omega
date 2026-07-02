// Fuente única de íconos válidos para pasos del proceso (nombre lucide en la columna `icon`).
// Lo consumen ProcessStepCard (render de la landing) y el editor de Proceso (dropdown · Checkpoint C).
// Los 4 sembrados usan UserPlus/Link/Sparkles/CheckCircle; el resto amplía el set del owner.
import {
  UserPlus,
  Link,
  Sparkles,
  CheckCircle,
  ClipboardCheck,
  Compass,
  Rocket,
  TrendingUp,
  Settings,
  Send,
  Calendar,
  Target,
  type LucideIcon,
} from "lucide-react";

export const PROCESS_ICONS: Record<string, LucideIcon> = {
  UserPlus,
  Link,
  Sparkles,
  CheckCircle,
  ClipboardCheck,
  Compass,
  Rocket,
  TrendingUp,
  Settings,
  Send,
  Calendar,
  Target,
};

export const PROCESS_ICON_NAMES = Object.keys(PROCESS_ICONS);

export const processIcon = (name: string): LucideIcon => PROCESS_ICONS[name] ?? ClipboardCheck;
