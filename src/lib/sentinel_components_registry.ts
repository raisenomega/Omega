// Registry canónico de los 10 componentes monitoreados por SENTINEL (V1 · hardcoded).
// sourceTable es DOCUMENTAL: el frontend lee vía endpoint FastAPI (AP-OMEGA-005), no la tabla.
// El texto whatItChecks de VAULT/PULSE/DB es la fuente de AGENT_CHECKS (verificado vs backend · P1).

export interface SentinelComponentMeta {
  readonly code: string;
  readonly name: string;
  readonly whatItChecks: string;
  readonly frequency: string;
  readonly sourceTable: string;
}

export const SENTINEL_COMPONENTS: readonly SentinelComponentMeta[] = [
  {
    code: "VAULT", name: "VAULT", frequency: "cron 2 AM AST", sourceTable: "sentinel_scans",
    whatItChecks: "Verifica variables de entorno críticas: que estén presentes, con formato válido y longitud mínima (secrets fuertes).",
  },
  {
    code: "PULSE_MONITOR", name: "PULSE_MONITOR", frequency: "cada 5 min", sourceTable: "sentinel_scans",
    whatItChecks: "Verifica endpoints críticos: detecta caídas (5xx), latencia alta y regresión de auth (un endpoint protegido que responde 200 sin token).",
  },
  {
    code: "DB_GUARDIAN", name: "DB_GUARDIAN", frequency: "cron 5 AM", sourceTable: "sentinel_scans",
    whatItChecks: "Verifica que las tablas críticas (agents, clients, resellers, etc.) sean accesibles y tengan los datos mínimos esperados.",
  },
  {
    code: "DEPENDENCY_SCAN", name: "Dependencias y CVEs", frequency: "on-push (GitHub Action)", sourceTable: "sentinel_dependency_scans",
    whatItChecks: "CVEs y vulnerabilidades en dependencias (npm + pip) reportadas por el GitHub Action de seguridad.",
  },
  {
    code: "SECRETS_ROTATION", name: "Rotación de secrets", frequency: "cron mensual", sourceTable: "sentinel_secrets_log",
    whatItChecks: "Antigüedad de secrets críticos: alerta cuando un secret supera su ventana de rotación recomendada.",
  },
  {
    code: "RLS_HARDENING", name: "RLS Hardening", frequency: "cron horario", sourceTable: "sentinel_rls_audits",
    whatItChecks: "Auditoría de Row Level Security: detecta tablas sin RLS activa o con políticas demasiado permisivas.",
  },
  {
    code: "AI_PROVIDER_ROUTER", name: "AI Providers", frequency: "tiempo real (por call)", sourceTable: "ai_provider_calls",
    whatItChecks: "Salud del router de proveedores IA: volumen de calls, éxito/fallo, latencia, failover y estado del circuit breaker.",
  },
  {
    code: "RUNTIME_OBSERVABILITY", name: "Observabilidad Runtime", frequency: "cada 5 min", sourceTable: "sentinel_runtime_scans",
    whatItChecks: "Errores de runtime backend/frontend: excepciones, error_rate, 5xx y patrones recurrentes en la ventana.",
  },
  {
    code: "PERFORMANCE_APM", name: "Performance / APM", frequency: "cada 5 min", sourceTable: "sentinel_performance_scans",
    whatItChecks: "Performance del sistema: p95/p99 por endpoint, slow queries y tamaño del bundle frontend.",
  },
  {
    code: "AGENTS_HEALTH", name: "Agentes IA · Health", frequency: "cron horario", sourceTable: "sentinel_agents_health_scans",
    whatItChecks: "Salud de los agentes IA: success_rate, accuracy, costo diario y detección de model drift.",
  },
] as const;
