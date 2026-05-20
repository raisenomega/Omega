// Root Zod schema · OnboardingForm type · alineado con OnboardingPayload Pydantic.
import { z } from "zod";
import {
  identitySchema, businessSchema, audienceSchema, brandVoiceSchema,
  goalsSchema, contentHistorySchema, socialAccountSchema,
  instructionsSchema, brandAssetsSchema,
} from "./onboarding-schema-sections";

export const onboardingSchema = z.object({
  identity: identitySchema,
  business: businessSchema.default({}),
  audience: audienceSchema.default({ competitors: [] }),
  brand_voice: brandVoiceSchema.default({
    brand_voice_keywords: [], avoided_words: [], preferred_formats: [],
  }),
  goals: goalsSchema.default({}),
  content_history: contentHistorySchema.default({
    has_existing_content: false, content_themes: [],
  }),
  social_accounts: z.array(socialAccountSchema).default([]),
  instructions: instructionsSchema.default({
    requires_publish_approval: true,
    preferred_publishing_hours: [],
    timezone: "America/Puerto_Rico",
  }),
  brand_assets: brandAssetsSchema.optional().nullable(),
  brand_voice_samples: z.array(z.string()).default([]),
});

export type OnboardingForm = z.infer<typeof onboardingSchema>;
