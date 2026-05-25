// Helper compartido · sectionsFilled boolean[] por las 10 secciones del Wizard.
// Usado por useOnboardingForm (percent) + OnboardingWizard (set para Stepper).
import type { OnboardingForm } from "./onboarding-schema";

// AUDIT 1: espejo EXACTO de backend calc_completion_percent (_onboarding_helpers.py).
// Antes los arrays vacíos (tone:[], goals.primary_goal:[]) eran truthy en JS → §3 y §4
// contaban como llenas siempre (form en blanco ya marcaba 20%) → el wizard mostraba 40%
// mientras el backend guardaba 20%. Ahora se chequea .length y los mismos campos que el back.
export function sectionsFilled(v: Partial<OnboardingForm>): boolean[] {
  const b = v.business, a = v.audience, bv = v.brand_voice, g = v.goals;
  const h = v.content_history, i = v.instructions, ba = v.brand_assets;
  return [
    !!(v.identity?.name && v.identity?.industry && (v.identity?.regions?.length ?? 0) > 0),
    !!(b?.niche || b?.business_what || b?.business_to_whom || b?.business_diff),
    !!(a?.target_audience || a?.audience_age_range || (a?.competitors?.length ?? 0) > 0),
    (bv?.tone?.length ?? 0) > 0 || (bv?.brand_voice_keywords?.length ?? 0) > 0 || (bv?.preferred_formats?.length ?? 0) > 0,
    (g?.primary_goal?.length ?? 0) > 0 || !!g?.goal_this_month || !!g?.success_metric,
    !!(h?.has_existing_content || h?.best_post_url || h?.what_worked),
    (v.social_accounts?.length ?? 0) > 0,
    !!(i?.custom_instructions || i?.emergency_contact_name) || (i?.preferred_publishing_hours?.length ?? 0) > 0,
    !!(ba && (ba.primary_color || ba.logo_file_id)),
    (v.brand_voice_samples?.length ?? 0) > 0,
  ];
}

export function completionPercent(filled: boolean[]): number {
  return Math.round((filled.filter(Boolean).length / filled.length) * 100);
}
