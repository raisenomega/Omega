import { ComingSoon } from "@/components/ComingSoon";

// DEBT-033: depende de `useOrganization` que consulta 5 tablas inexistentes
// en V3 (profiles, organizations, user_roles, audit_logs, plus profiles team).
// Re-modelado de organización/team/RBAC pendiente Fase 3 §3.x.
export default function SettingsPage() {
  return (
    <ComingSoon
      title="Configuración"
      message="La gestión de organización, equipo, roles y bitácora está siendo reconstruida. El logout sigue disponible desde el sidebar."
    />
  );
}
