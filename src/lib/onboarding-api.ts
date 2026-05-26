import type { OnboardingForm } from "./onboarding-schema";
import { apiGet, apiPost, apiPatch, apiPostFormData } from "./api-client";

interface OnboardingResponse {
  client_id: string;
  completion_percent: number;
  onboarding_complete: boolean;
}

// DEBT-059: categorías válidas del backend (handler ALLOWED_CATEGORIES + CHECK 00011).
export type BrandFileCategory = "logo" | "brand_guide" | "sample_content" | "other";

// Sube un archivo de marca a brand_files vía POST /clients/{id}/brand-files.
// Devuelve el id de la fila creada (para enlazar client_brand_assets.logo_file_id).
export async function uploadBrandFile(
  clientId: string, file: File, category: BrandFileCategory,
): Promise<{ id: string }> {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("file_category", category);
  return apiPostFormData<{ id: string }>(`/clients/${clientId}/brand-files`, fd);
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
