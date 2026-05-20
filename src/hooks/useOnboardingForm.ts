import { useForm, type UseFormReturn } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "./use-toast";
import { onboardingSchema, type OnboardingForm } from "@/lib/onboarding-schema";
import { sectionsFilled, completionPercent } from "@/lib/onboarding-completion";

const DEFAULTS: Partial<OnboardingForm> = {
  business: {} as OnboardingForm["business"],
  audience: { competitors: [] } as OnboardingForm["audience"],
  brand_voice: { brand_voice_keywords: [], avoided_words: [], preferred_formats: [] } as OnboardingForm["brand_voice"],
  goals: {} as OnboardingForm["goals"],
  content_history: { has_existing_content: false, content_themes: [] } as OnboardingForm["content_history"],
  social_accounts: [],
  instructions: { requires_publish_approval: true, preferred_publishing_hours: [], timezone: "America/Puerto_Rico" } as OnboardingForm["instructions"],
  brand_assets: null,
  brand_voice_samples: [],
};

export interface UseOnboardingFormResult {
  form: UseFormReturn<OnboardingForm>;
  submit: () => void;
  isSubmitting: boolean;
  completionPercent: number;
}

export function useOnboardingForm(onSuccess?: (clientId: string) => void): UseOnboardingFormResult {
  const { toast } = useToast();
  const form = useForm<OnboardingForm>({
    resolver: zodResolver(onboardingSchema),
    defaultValues: DEFAULTS as OnboardingForm,
    mode: "onChange",
  });

  const values = form.watch();
  const pct = completionPercent(sectionsFilled(values));

  const mutation = useMutation({
    mutationFn: async (data: OnboardingForm) => {
      const { data: { session } } = await supabase.auth.getSession();
      const base = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
      const res = await fetch(`${base}/clients/onboarding`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${session?.access_token ?? ""}` },
        body: JSON.stringify(data),
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(typeof e.detail === "string" ? e.detail : `HTTP ${res.status}`); }
      return res.json() as Promise<{ client_id: string; completion_percent: number; onboarding_complete: boolean }>;
    },
    onSuccess: (r) => { toast({ title: "Cliente creado", description: `Onboarding ${r.completion_percent}% · ${r.onboarding_complete ? "completo" : "parcial"}` }); onSuccess?.(r.client_id); },
    onError: (e: Error) => toast({ title: "No se pudo guardar", description: e.message, variant: "destructive" }),
  });

  return {
    form,
    submit: form.handleSubmit((data) => mutation.mutate(data)),
    isSubmitting: mutation.isPending,
    completionPercent: pct,
  };
}
