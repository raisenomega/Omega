// Helpers de fecha del calendario (string YYYY-MM-DD · UTC · sin TZ shift). Reusados por
// WeekView (semana) y DayView (navegación día). Cero dependencia de dato/backend.

export function isoDate(dt: Date): string {
  return dt.toISOString().slice(0, 10);
}

// Suma n días a un day-key (YYYY-MM-DD) y devuelve otro day-key.
export function addDays(day: string, n: number): string {
  const [y, m, d] = day.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  dt.setUTCDate(dt.getUTCDate() + n);
  return isoDate(dt);
}

// Lunes de la semana que contiene day (Lun=0).
export function startOfWeek(day: string): string {
  const [y, m, d] = day.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  dt.setUTCDate(dt.getUTCDate() - ((dt.getUTCDay() + 6) % 7));
  return isoDate(dt);
}
