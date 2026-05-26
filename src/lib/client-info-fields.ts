// DEBT-054 · Info Tab del cliente · arma las filas del client_context (wizard) que SÍ
// tienen valor (dinámico · sin huecos). Acceso anidado por sección · read-only.
import type { OnboardingForm } from "./onboarding-schema";
import { REGION_LABELS, type Region } from "./client-constants";

export interface InfoRow {
  label: string;
  value: string;
  chips?: string[];  // DEBT-042: si presente, el Info Tab renderiza chips en vez de texto.
}

function joinArr(x: unknown): string {
  return Array.isArray(x) ? x.filter(Boolean).join(", ") : "";
}

// DEBT-042: regiones (códigos PR/USA/...) → labels legibles para chips.
function regionLabels(x: unknown): string[] {
  return Array.isArray(x)
    ? x.filter(Boolean).map((r) => REGION_LABELS[r as Region] ?? String(r))
    : [];
}

function joinCompetitors(x: unknown): string {
  if (!Array.isArray(x)) return "";
  return x
    .map((c) => (c && typeof c === "object" ? String((c as { name?: string }).name ?? "") : ""))
    .filter(Boolean)
    .join(", ");
}

/** Filas del client_context con valor · solo las pobladas (refleja el % real del perfil). */
export function buildContextRows(d: OnboardingForm | undefined): InfoRow[] {
  if (!d) return [];
  const regions = regionLabels(d.identity?.regions);
  const rows: InfoRow[] = [
    { label: "Sitio web", value: d.identity?.website ?? "" },
    { label: "Email de negocio", value: d.identity?.business_email ?? "" },
    { label: "Regiones", value: regions.join(", "), chips: regions.length ? regions : undefined },
    { label: "Nicho", value: d.business?.niche ?? "" },
    { label: "Vertical", value: d.business?.vertical ?? "" },
    { label: "Qué hace", value: d.business?.business_what ?? "" },
    { label: "A quién", value: d.business?.business_to_whom ?? "" },
    { label: "Diferenciador", value: d.business?.business_diff ?? "" },
    { label: "Audiencia", value: d.audience?.target_audience ?? "" },
    { label: "Rango de edad", value: d.audience?.audience_age_range ?? "" },
    { label: "Género audiencia", value: d.audience?.audience_gender ?? "" },
    { label: "Competidores", value: joinCompetitors(d.audience?.competitors) },
    { label: "Voz / tono", value: joinArr(d.brand_voice?.tone) },
    { label: "Objetivos", value: joinArr(d.goals?.primary_goal) },
  ];
  return rows.filter((r) => r.value.trim().length > 0);
}
