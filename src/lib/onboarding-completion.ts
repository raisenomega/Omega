// Helper compartido · sectionsFilled boolean[] por las 10 secciones del Wizard.
// Usado por useOnboardingForm (percent) + OnboardingWizard (set para Stepper).
import type { OnboardingForm } from "./onboarding-schema";

export function sectionsFilled(v: Partial<OnboardingForm>): boolean[] {
  return [
    !!(v.identity?.name && v.identity?.industry && v.identity?.region),
    !!(v.business && Object.values(v.business).some((x) => x)),
    !!(v.audience?.target_audience || (v.audience?.competitors?.length ?? 0) > 0),
    !!(v.brand_voice?.tone || (v.brand_voice?.brand_voice_keywords?.length ?? 0) > 0),
    !!(v.goals && Object.values(v.goals).some((x) => x)),
    !!(v.content_history?.has_existing_content || v.content_history?.best_post_url),
    (v.social_accounts?.length ?? 0) > 0,
    !!(v.instructions?.custom_instructions || v.instructions?.emergency_contact_name),
    !!(v.brand_assets && (v.brand_assets.primary_color || v.brand_assets.logo_file_id)),
    (v.brand_voice_samples?.length ?? 0) > 0,
  ];
}

export function completionPercent(filled: boolean[]): number {
  return Math.round((filled.filter(Boolean).length / filled.length) * 100);
}
