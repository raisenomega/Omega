import { useMutation } from "@tanstack/react-query";

// DEBT-033: las 5 tablas que este hook consultaba NO existen en schema V3:
// profiles, organizations, user_roles, audit_logs. Las queries originales
// generaban ~15 errores de console por session. Stub mientras se diseña el
// modelo de organización/team/RBAC V3 en Fase 3 §3.x.
//
// SettingsPage.tsx ahora renderiza <ComingSoon /> (DEBT-033) y no consume
// estos campos. Mantenemos la firma del hook por si algún call site externo
// aún lo importa, pero todo retorna empty/no-op.

interface StubOrgData {
  loading: boolean;
  profile: null;
  organization: null;
  team: never[];
  auditLogs: never[];
  updateOrg: ReturnType<typeof useMutation<void, Error, unknown>>;
  updateRole: ReturnType<typeof useMutation<void, Error, unknown>>;
  isAdmin: boolean;
}

export function useOrganization(): StubOrgData {
  const updateOrg = useMutation<void, Error, unknown>({
    mutationFn: async () => {
      throw new Error("Organización no disponible · DEBT-033");
    },
  });

  const updateRole = useMutation<void, Error, unknown>({
    mutationFn: async () => {
      throw new Error("Roles no disponibles · DEBT-033");
    },
  });

  return {
    loading: false,
    profile: null,
    organization: null,
    team: [],
    auditLogs: [],
    updateOrg,
    updateRole,
    isAdmin: false,
  };
}
