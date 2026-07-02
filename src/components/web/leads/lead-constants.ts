// Constantes del CRM de leads · réplica del molde (colores/labels) + adaptación OMEGA:
// status de OMEGA (5) con etiquetas ES (D3) · temperatura (D1) · audience (D5) · wa.me (D6).
export const STATUSES = ["new", "contacted", "qualified", "converted", "lost"];
export const TEMPERATURES = ["frio", "tibio", "caliente", "convertido"];

export const STATUS_LABELS: Record<string, string> = {
  new: "Nuevo", contacted: "Contactado", qualified: "Calificado", converted: "Convertido", lost: "Perdido",
};
export const STATUS_COLORS: Record<string, string> = {
  new: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  contacted: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  qualified: "bg-green-500/20 text-green-400 border-green-500/30",
  converted: "bg-primary/20 text-primary border-primary/30",
  lost: "bg-muted text-muted-foreground border-border",
};
export const TEMP_LABELS: Record<string, string> = {
  frio: "❄️ Frío", tibio: "🌤 Tibio", caliente: "🔥 Caliente", convertido: "⭐ Convertido",
};
export const TEMP_COLORS: Record<string, string> = {
  frio: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
  tibio: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  caliente: "bg-red-500/20 text-red-400 border-red-500/30",
  convertido: "bg-primary/20 text-primary border-primary/30",
};
export const AUDIENCE_LABELS: Record<string, string> = { pyme: "PYME", reseller: "Agencia" };

// D6 · click-to-chat wa.me: prioriza phone (solo dígitos) · si no hay, username · null → botón disabled.
export function waLink(lead: { phone: string | null; whatsapp_username: string | null }): string | null {
  const digits = lead.phone?.replace(/\D/g, "");
  if (digits) return `https://wa.me/${digits}`;
  if (lead.whatsapp_username) return `https://wa.me/${lead.whatsapp_username}`;
  return null;
}
