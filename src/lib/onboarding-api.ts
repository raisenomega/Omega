import type { OnboardingForm } from "./onboarding-schema";
import { apiGet, apiPost, apiPatch } from "./api-client";

interface OnboardingResponse {
  client_id: string;
  completion_percent: number;
  onboarding_complete: boolean;
}

export async function fetchOnboardingData(clientId: string): Promise<OnboardingForm> {
  return apiGet<OnboardingForm>(`/clients/${clientId}/onboarding-data`);
}

export async function postOnboarding(data: OnboardingForm): Promise<OnboardingResponse> {
  return apiPost<OnboardingResponse>(`/clients/onboarding`, data);
}

export async function patchOnboarding(clientId: string, data: OnboardingForm): Promise<OnboardingResponse> {
  return apiPatch<OnboardingResponse>(`/clients/${clientId}/onboarding-data`, data);
}
