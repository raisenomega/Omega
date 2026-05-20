// Sync manual con backend/app/domain/{client_constants,social_platforms}.py
// Owner decisions 2026-05-20 · ver DDD A2 + spec wizard onboarding.

export const BUSINESS_SIZES = ["solo", "pequeno", "mediano", "grande"] as const;

export const TONES = [
  "profesional", "casual", "divertido", "tecnico", "inspirador", "autoritario",
] as const;

export const EMOJI_USAGE = ["never", "rarely", "balanced", "frequent"] as const;

export const HASHTAG_STRATEGY = ["minimal", "balanced", "many"] as const;

export const PRIMARY_GOALS = [
  "awareness", "leads", "sales", "community", "retention",
] as const;

export const AUDIENCE_AGE_RANGES = [
  "13-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+",
] as const;

export const GENDERS = ["male", "female", "mixed", "non_binary", "any"] as const;

export const CONTENT_FORMATS = [
  "carousel", "reels", "photos", "long_video", "stories",
] as const;

export const PUBLISHING_FREQUENCIES = [
  "daily", "few_per_week", "weekly", "biweekly", "monthly", "irregular",
] as const;

export const PLATFORMS = [
  "instagram", "facebook", "tiktok", "twitter", "linkedin", "youtube",
] as const;

export const PLATFORM_LABELS: Record<typeof PLATFORMS[number], string> = {
  instagram: "Instagram",
  facebook: "Facebook",
  tiktok: "TikTok",
  twitter: "X (Twitter)",
  linkedin: "LinkedIn",
  youtube: "YouTube",
};

export type Tone = typeof TONES[number];
export type Platform = typeof PLATFORMS[number];
