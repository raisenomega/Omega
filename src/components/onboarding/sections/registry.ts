import type { ComponentType } from "react";
import type { UseFormReturn } from "react-hook-form";
import type { OnboardingForm } from "@/lib/onboarding-schema";
import { SectionIdentity } from "./SectionIdentity";
import { SectionBusiness } from "./SectionBusiness";
import { SectionAudience } from "./SectionAudience";
import { SectionBrandVoice } from "./SectionBrandVoice";
import { SectionGoals } from "./SectionGoals";
import { SectionContentHistory } from "./SectionContentHistory";
import { SectionSocialAccounts } from "./SectionSocialAccounts";
import { SectionInstructions } from "./SectionInstructions";
import { SectionBrandAssets } from "./SectionBrandAssets";
import { SectionSamples } from "./SectionSamples";

export interface SectionDef {
  id: string;
  title: string;
  required?: boolean;
  Component: ComponentType<{ form: UseFormReturn<OnboardingForm> }>;
}

export const SECTIONS: readonly SectionDef[] = [
  { id: "identity", title: "Identidad", required: true, Component: SectionIdentity },
  { id: "business", title: "Negocio", Component: SectionBusiness },
  { id: "audience", title: "Audiencia", Component: SectionAudience },
  { id: "brand_voice", title: "Voz de marca", Component: SectionBrandVoice },
  { id: "goals", title: "Objetivos", Component: SectionGoals },
  { id: "content_history", title: "Historial de contenido", Component: SectionContentHistory },
  { id: "social_accounts", title: "Cuentas sociales", Component: SectionSocialAccounts },
  { id: "instructions", title: "Instrucciones especiales", Component: SectionInstructions },
  { id: "brand_assets", title: "Identidad visual", Component: SectionBrandAssets },
  { id: "samples", title: "Ejemplos de contenido", Component: SectionSamples },
] as const;
