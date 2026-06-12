/**
 * Convierte la hora LOCAL del usuario (del input datetime-local, sin offset) a
 * un ISO UTC explícito (con Z) antes de enviarla al backend. Bug tz (11 jun):
 * mandar el string naive hacía que el backend lo guardara como UTC → corrimiento
 * de -4h en AST (owner escribe 09:45 → calendario muestra 05:45). El usuario
 * siempre quiere SU hora local; el contrato con el backend es UTC explícito.
 */
export function toUtcIso(localDateTime: string): string {
  // new Date("YYYY-MM-DDTHH:mm") interpreta el string SIN offset como hora LOCAL
  // del navegador → toISOString() lo convierte a UTC con Z.
  return new Date(localDateTime).toISOString();
}
