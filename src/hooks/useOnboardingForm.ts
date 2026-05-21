import { useEffect } from "react";
import { useForm, type UseFormReturn } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useToast } from "./use-toast";
import { onboardingSchema, type OnboardingForm } from "@/lib/onboarding-schema";
import { sectionsFilled, completionPercent } from "@/lib/onboarding-completion";
import { fetchOnboardingData, postOnboarding, patchOnboarding } from "@/lib/onboarding-api";

const DEFAULTS: Partial<OnboardingForm> = {
  business: {} as OnboardingForm["business"],
  audience: { competitors: [] } as OnboardingForm["audience"],
  brand_voice: { tone: [], brand_voice_keywords: [], avoided_words: [], preferred_formats: [] } as OnboardingForm["brand_voice"],
  goals: { primary_goal: [] } as OnboardingForm["goals"],
  content_history: { has_existing_content: false, content_themes: [] } as OnboardingForm["content_history"],
  social_accounts: [],
  instructions: { requires_publish_approval: true, preferred_publishing_hours: [], timezone: "America/Puerto_Rico" } as OnboardingForm["instructions"],
  brand_assets: null,
  brand_voice_samples: [],
};

export interface UseOnboardingFormOptions { clientId?: string | null; onSuccess?: (clientId: string) => void; }
export interface UseOnboardingFormResult {
  form: UseFormReturn<OnboardingForm>; submit: () => void;
  isSubmitting: boolean; isLoading: boolean; isEditing: boolean; completionPercent: number;
  isError: boolean; errorMessage: string | null; retry: () => void;
}

export function useOnboardingForm(opts: UseOnboardingFormOptions = {}): UseOnboardingFormResult {
  const { toast } = useToast();
  const { clientId, onSuccess } = opts;
  const isEditing = !!clientId;

  const form = useForm<OnboardingForm>({
    resolver: zodResolver(onboardingSchema),
    defaultValues: DEFAULTS as OnboardingForm,
    mode: "onChange",
  });

  const dataQuery = useQuery({
    queryKey: ["client_onboarding_data", clientId],
    queryFn: () => fetchOnboardingData(clientId!),
    enabled: isEditing,
    retry: 1,
  });

  useEffect(() => {
    if (dataQuery.data) form.reset(dataQuery.data);
  }, [dataQuery.data, form]);

  const pct = completionPercent(sectionsFilled(form.watch()));

  const mutation = useMutation({
    mutationFn: (data: OnboardingForm) => (clientId ? patchOnboarding(clientId, data) : postOnboarding(data)),
    onSuccess: (r) => {
      toast({ title: isEditing ? "Cliente actualizado" : "Cliente creado", description: `${r.completion_percent}% · ${r.onboarding_complete ? "completo" : "parcial"}` });
      onSuccess?.(r.client_id);
    },
    onError: (e: Error) => toast({ title: isEditing ? "No se pudo actualizar" : "No se pudo crear", description: e.message, variant: "destructive" }),
  });

  return {
    form,
    submit: form.handleSubmit((d) => mutation.mutate(d)),
    isSubmitting: mutation.isPending,
    isLoading: isEditing && dataQuery.isLoading,
    isEditing,
    completionPercent: pct,
    isError: isEditing && dataQuery.isError,
    errorMessage: dataQuery.error instanceof Error ? dataQuery.error.message : null,
    retry: () => dataQuery.refetch(),
  };
}
