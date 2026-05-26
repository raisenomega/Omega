import type { WebAnalysis } from "@/hooks/useWebAnalysis";
import type { GeoCheck, GeoStatus } from "@/hooks/useGeoCheck";

const GEO_LABEL: Record<GeoStatus, string> = {
  appeared: "Aparecés en ChatGPT",
  partial: "Aparecés parcialmente en ChatGPT",
  not_appeared: "No aparecés en ChatGPT",
  unknown: "Visibilidad IA sin verificar",
};

export function geoStatusLabel(status: GeoStatus): string {
  return GEO_LABEL[status];
}

// Arma un brief de texto con los hallazgos · se pre-carga en el topic del Content Lab
export function buildIntelligenceBrief(web?: WebAnalysis, geo?: GeoCheck): string {
  const lines: string[] = ["Brief de inteligencia"];

  if (web?.analyzed) {
    lines.push(`Score SEO: ${web.score}/100`);
    const kw = web.keywords.slice(0, 3);
    if (kw.length) lines.push(`Keywords: ${kw.join(", ")}`);
    const gaps = web.recommendations.slice(0, 3);
    if (gaps.length) lines.push(`Gaps: ${gaps.join(" · ")}`);
  } else {
    lines.push("Sitio web sin analizar aún");
  }

  lines.push(`Visibilidad IA: ${geo ? geoStatusLabel(geo.status) : "sin verificar"}`);
  return lines.join("\n");
}
