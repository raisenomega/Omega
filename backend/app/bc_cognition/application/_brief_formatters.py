"""Formatters puros de briefs (DEBT-105) · sin I/O · convierten dict -> (subject, body).

Separado de brief_dispatcher para mantener cada módulo <=75L (C4) y aislar la lógica
de formato (pura, testeable) del envío (I/O httpx). Strings sin emojis (project-wide).
"""
from typing import Any


def format_sentinel(result: dict[str, Any]) -> tuple[str, str]:
    score, status = result.get("security_score", 0), result.get("status", "?")
    issues = result.get("issues", [])
    lines = [f"- [{i.get('severity', '?')}] "
             f"{i.get('message') or i.get('title') or i.get('agent_code') or 'issue'}"
             for i in issues[:15]]
    detail = "\n".join(lines) if lines else "- sin issues"
    subject = f"OMEGA SENTINEL brief diario · score {score}/100 · {status}"
    body = (f"SENTINEL brief diario\n"
            f"Score: {score}/100 ({status}) · decision: {result.get('deploy_decision', '?')}\n"
            f"Issues: {result.get('total_issues', 0)} "
            f"({result.get('critical_issues', 0)} CRITICAL) · "
            f"agentes: {result.get('agents_scanned', 0)}\n\n{detail}")
    return subject, body


def format_oracle(brief: dict[str, Any]) -> tuple[str, str]:
    es = brief.get("executive_summary", {})
    opps = brief.get("opportunities", [])
    alerts = brief.get("alerts", [])
    opp_lines = "\n".join(f"- [{o.get('priority', '?')}] {o.get('description', '')}"
                          for o in opps) or "- ninguna"
    alert_lines = "\n".join(f"- [{a.get('severity', '?')}] {a.get('description', '')}"
                            for a in alerts) or "- ninguna"
    subject = f"OMEGA ORACLE brief semanal · {brief.get('week_of', '')}"
    body = (f"ORACLE brief semanal · semana del {brief.get('week_of', '?')}\n\n"
            f"Clientes: {es.get('total_clients', 0)} ({es.get('active_clients', 0)} activos)\n"
            f"Resellers: {es.get('total_resellers', 0)} · "
            f"SENTINEL score: {es.get('sentinel_score')}\n\n"
            f"Oportunidades ({len(opps)}):\n{opp_lines}\n\n"
            f"Alertas ({len(alerts)}):\n{alert_lines}\n\n"
            f"Recomendacion: {brief.get('recommendation', '')}")
    return subject, body
