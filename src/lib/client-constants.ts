// Sync manual con backend/app/domain/client_constants.py (DDD A2)
// Owner decision 2026-05-20: 8 industries PYME-core + 8 países LATAM
export const INDUSTRIES = [
  "retail", "restaurante", "servicios", "salud",
  "educacion", "tecnologia", "inmobiliaria", "otros",
] as const;

export const REGIONS = [
  "PR", "USA", "DO", "MX", "CO", "AR", "ES", "otros",
] as const;

export type Industry = typeof INDUSTRIES[number];
export type Region = typeof REGIONS[number];

// DEBT-042: labels legibles para mostrar las regiones como chips (no códigos crudos).
export const REGION_LABELS: Record<Region, string> = {
  PR: "Puerto Rico", USA: "Estados Unidos", DO: "Rep. Dominicana", MX: "México",
  CO: "Colombia", AR: "Argentina", ES: "España", otros: "Otros",
};
