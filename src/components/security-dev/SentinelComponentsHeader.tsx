import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// Qué chequea cada agente SENTINEL · texto VERIFICADO contra backend/app/services/sentinel_*.py (P1).
// VAULT: solo env vars (NO código ni commits). DB_GUARDIAN: solo accesibilidad+conteos (NO RLS/migraciones).
export const AGENT_CHECKS: Record<string, string> = {
  VAULT: "Verifica variables de entorno críticas: que estén presentes, con formato válido y longitud mínima (secrets fuertes).",
  PULSE_MONITOR: "Verifica endpoints críticos: detecta caídas (5xx), latencia alta y regresión de auth (un endpoint protegido que responde 200 sin token).",
  DB_GUARDIAN: "Verifica que las tablas críticas (agents, clients, resellers, etc.) sean accesibles y tengan los datos mínimos esperados.",
};

export function SentinelComponentsHeader() {
  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Componentes monitoreados</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {Object.entries(AGENT_CHECKS).map(([agent, desc]) => (
          <div key={agent} className="text-sm">
            <span className="font-medium">{agent}</span>
            <p className="text-xs text-muted-foreground">{desc}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
