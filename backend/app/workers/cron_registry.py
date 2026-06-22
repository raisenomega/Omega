"""Fuente única del inventario de cron jobs · P1-5 (Fase 2).

main.py registra estos jobs en el scheduler (startup) · el endpoint
/system/cron-status compara los jobs activos contra esta lista · el test asserta
que los `add_job` de main.py == este set (drift falla en CI). Cierra el drift
documental de DDD X3 (decía 8/16). Verificado 16 jun: 24 crons reales (el "25"
del grep era `add_jobstore`, no un cron · el "21" excluía ids con dígitos)."""
from typing import Final

CRON_JOB_IDS: Final[frozenset[str]] = frozenset({
    "vault_scan", "db_guardian", "sentinel_brief", "pulse_monitor",
    "oracle_weekly_brief", "aria_learning_report", "news_monitor",
    "competitor_tracker", "trend_spotter", "brand_dna_refresh",
    "video_jobs_orphan_cleanup", "outcome_evaluator", "credit_period_reset",
    "decision_evaluator", "strategy_generator", "hermes_ping",
    "secrets_rotation_monthly", "rls_audit_hourly", "runtime_observability_5min",
    "performance_5min", "agents_health_hourly", "network_http_2h",
    "integrations_hourly", "chaos_monthly",
    "rex_publisher",  # DEBT-098 · publicador autónomo REX · cada 5 min (20 jun · 24→25)
    "hermes_alert_check",  # HERMES nivel 2 · alerta inmediata integración crítica caída (21 jun · 25→26)
    "social_metrics_snapshot",  # Arco 1 · histórico social organic · diario 6am UTC (22 jun · 26→27)
})

EXPECTED_CRON_JOBS: Final[int] = len(CRON_JOB_IDS)

assert EXPECTED_CRON_JOBS == 27, f"cron_registry: esperado 27, hay {EXPECTED_CRON_JOBS}"
