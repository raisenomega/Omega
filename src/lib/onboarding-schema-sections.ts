// Zod sub-schemas · 9 secciones · alineado 1:1 con backend Pydantic.
// BUG A (defensivo): data cargada/legacy inválida NUNCA bloquea el save (onInvalid).
// enum desconocido → null · array de enums inválida → [] · hex/uuid inválido → null ·
// competitors legacy string[] → {name,url}[]. Lo válido se conserva; el save procede.
import { z } from "zod";
import { INDUSTRIES, REGIONS } from "./client-constants";
import {
  BUSINESS_SIZES, TONES, EMOJI_USAGE, HASHTAG_STRATEGY, PRIMARY_GOALS,
  AUDIENCE_AGE_RANGES, GENDERS, CONTENT_FORMATS, PUBLISHING_FREQUENCIES, PLATFORMS,
} from "./onboarding-constants";

const opt = <T extends z.ZodTypeAny>(s: T) => s.optional().nullable();
const hex = z.string().regex(/^#[0-9A-Fa-f]{6}$/);
const intMin0 = z.coerce.number().int().min(0);

export const identitySchema = z.object({
  name: z.string().min(1, "Requerido").max(120),
  industry: z.enum(INDUSTRIES),
  regions: z.array(z.enum(REGIONS)).min(1, "Selecciona al menos una"),
});

export const businessSchema = z.object({
  niche: opt(z.string()), vertical: opt(z.string()),
  business_what: opt(z.string()), business_to_whom: opt(z.string()), business_diff: opt(z.string()),
  business_size: opt(z.enum(BUSINESS_SIZES)).catch(null), years_operating: opt(intMin0).catch(null),
});

export const audienceSchema = z.object({
  target_audience: opt(z.string()),
  audience_age_range: opt(z.string()),
  audience_gender: opt(z.enum(GENDERS)).catch(null),
  competitors: z.preprocess(
    (val) => (Array.isArray(val) ? val.map((c) => (typeof c === "string" ? { name: c, url: null } : c)) : val),
    z.array(z.object({ name: z.string(), url: opt(z.string()) })),
  ).default([]).catch([]),
});

export const brandVoiceSchema = z.object({
  tone: z.array(z.enum(TONES)).default([]).catch([]),
  brand_voice_keywords: z.array(z.string()).default([]),
  avoided_topics: opt(z.string()), avoided_words: z.array(z.string()).default([]),
  preferred_formats: z.array(z.enum(CONTENT_FORMATS)).default([]).catch([]),
  emoji_usage: opt(z.enum(EMOJI_USAGE)).catch(null), hashtag_strategy: opt(z.enum(HASHTAG_STRATEGY)).catch(null),
});

export const goalsSchema = z.object({
  primary_goal: z.array(z.enum(PRIMARY_GOALS)).max(3).default([]).catch([]),
  goal_this_month: opt(z.string()), goal_this_quarter: opt(z.string()),
  goal_priority_now: opt(z.string()), success_metric: opt(z.string()),
  monthly_revenue_target: opt(z.coerce.number().min(0)),
});

export const contentHistorySchema = z.object({
  has_existing_content: z.boolean().default(false), existing_followers: opt(intMin0),
  best_post_url: opt(z.string()), what_worked: opt(z.string()), what_failed: opt(z.string()),
  content_themes: z.array(z.string()).default([]),
});

export const socialAccountSchema = z.object({
  platform: z.enum(PLATFORMS), username: z.string().min(1).max(500).catch(""),
  profile_url: opt(z.string()), is_primary: z.boolean().default(false),
  auto_publish_allowed: z.boolean().default(false), approx_followers: opt(intMin0),
  publishing_frequency: opt(z.enum(PUBLISHING_FREQUENCIES)).catch(null),
  is_business_account: z.boolean().default(false),
  is_paused: z.boolean().default(false),
});

export const instructionsSchema = z.object({
  custom_instructions: opt(z.string()),
  emergency_contact_name: opt(z.string()), emergency_contact_phone: opt(z.string()),
  requires_publish_approval: z.boolean().default(true),
  preferred_publishing_hours: z.array(z.coerce.number().int().min(0).max(23)).default([]),
  timezone: z.string().default("America/Puerto_Rico"),
});

export const brandAssetsSchema = z.object({
  primary_color: opt(hex).catch(null), secondary_color: opt(hex).catch(null), accent_color: opt(hex).catch(null),
  font_primary: opt(z.string()), font_secondary: opt(z.string()),
  logo_file_id: opt(z.string().uuid()).catch(null), brand_guide_file_id: opt(z.string().uuid()).catch(null),
  logo_files: z.array(z.instanceof(File)).max(3).optional(),
});
