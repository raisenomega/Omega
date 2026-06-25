/** Constantes UI Content Lab · centralizadas para reuso (page + futuros sub-componentes). */

export const TYPES = [
  "caption", "hashtags", "video_script", "image", "video",
  "email", "story", "ad", "bio", "google_business_post",
  "thread", "carousel",
] as const;

export const TONES = ["profesional", "casual", "inspirador", "educativo", "divertido"] as const;
export const STYLES = ["realistic", "cartoon", "minimal"] as const;
export const RATIOS = ["1280:768", "768:1280"] as const;

export const TYPE_LABELS = {
  caption: "Caption", hashtags: "Hashtags", video_script: "Video Script",
  image: "Imagen", video: "Video", email: "Email", story: "Story",
  ad: "Ad Copy", bio: "Bio", google_business_post: "Google Business",
  thread: "Thread", carousel: "Carousel",
} as const;

export const TONE_LABELS = {
  profesional: "Profesional", casual: "Casual", inspirador: "Inspirador",
  educativo: "Educativo", divertido: "Divertido",
} as const;

export const STYLE_LABELS = { realistic: "Realista", cartoon: "Cartoon", minimal: "Minimal" } as const;
export const RATIO_LABELS = { "1280:768": "Horizontal 16:9", "768:1280": "Vertical 9:16" } as const;
