import { Sparkles, Mic, BarChart3, AlertTriangle, CalendarDays, Image as ImageIcon } from "lucide-react";
import type { LucideIcon } from "lucide-react";

export type PlanCode = "adopcion" | "basic" | "pro" | "enterprise";
export type Network = "instagram" | "facebook" | "tiktok" | "linkedin";

export interface PlanFeature {
  key: string;
  label: string;
  icon: LucideIcon;
  unlockedIn: PlanCode[];
  addonPrice?: number;
}

export interface PlanConfig {
  code: PlanCode;
  label: string;
  priceLabel: string;
  postsPerCycle: number;
  accountsPerNetwork: number;
}

export const NETWORKS: readonly Network[] = ["instagram", "facebook", "tiktok", "linkedin"];

export const FEATURES: PlanFeature[] = [
  { key: "content_lab", label: "Content Lab", icon: Sparkles, unlockedIn: ["adopcion","basic","pro","enterprise"] },
  { key: "brand_voice", label: "Brand Voice", icon: Mic, unlockedIn: ["adopcion","basic","pro","enterprise"] },
  { key: "analytics", label: "Analytics", icon: BarChart3, unlockedIn: ["adopcion","pro","enterprise"] },
  { key: "crisis_room", label: "Crisis Room", icon: AlertTriangle, unlockedIn: ["adopcion","pro","enterprise"], addonPrice: 25 },
  { key: "calendar", label: "Calendario", icon: CalendarDays, unlockedIn: ["adopcion","pro","enterprise"] },
  { key: "media", label: "Media", icon: ImageIcon, unlockedIn: ["adopcion","pro","enterprise"] },
];

export const PLAN_CONFIGS: Record<PlanCode, PlanConfig> = {
  adopcion: { code: "adopcion", label: "Adopción", priceLabel: "7 días gratis", postsPerCycle: 7, accountsPerNetwork: 1 },
  basic: { code: "basic", label: "Plan BÁSICO", priceLabel: "$29/mes", postsPerCycle: 32, accountsPerNetwork: 1 },
  pro: { code: "pro", label: "Plan PRO", priceLabel: "$65/mes", postsPerCycle: 64, accountsPerNetwork: 2 },
  enterprise: { code: "enterprise", label: "Plan ENTERPRISE", priceLabel: "personalizado", postsPerCycle: Infinity, accountsPerNetwork: Infinity },
};

export function getPlanConfig(plan: string): PlanConfig {
  if (plan in PLAN_CONFIGS) return PLAN_CONFIGS[plan as PlanCode];
  return PLAN_CONFIGS.basic;
}

export function getUnlockedFeatures(plan: PlanCode): PlanFeature[] {
  return FEATURES.filter((f) => f.unlockedIn.includes(plan));
}

export function getLockedFeatures(plan: PlanCode): PlanFeature[] {
  return FEATURES.filter((f) => !f.unlockedIn.includes(plan));
}
