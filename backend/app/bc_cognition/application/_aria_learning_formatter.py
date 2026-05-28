"""ARIA Learning Report formatter (DEBT-101) · dict → (subject, body) plaintext.

Tono ejecutivo · no técnico. Si no hay clientes activos → retorna None (worker skip email · cero ruido).
"""
from typing import Any, Optional


def format_aria_learning(report: dict[str, Any]) -> Optional[tuple[str, str]]:
    """(subject, body) o None si no hay actividad esa semana."""
    clients = report.get("clients") or []
    if not clients:
        return None
    week_of = report.get("week_of", "?")
    subject = f"ARIA Learning Report · semana del {week_of}"
    lines = [f"ARIA Learning Report · semana del {week_of}",
             f"Clientes con actividad: {len(clients)}", ""]
    for c in clients:
        name = c.get("client_name", "Cliente")
        total = c.get("decisions_total", 0)
        correct = c.get("correct", 0)
        incorrect = c.get("incorrect", 0)
        pending = c.get("pending", 0)
        evaluated = correct + incorrect
        accuracy = f"{round(100 * correct / evaluated)}%" if evaluated > 0 else "pendiente evaluacion"
        top = c.get("top_agents") or []
        tp = c.get("training_pairs_generated", 0)
        lines.append(f"== {name} ==")
        lines.append(f"  Decisiones: {total} ({correct} acertadas · {incorrect} erradas · {pending} sin evaluar)")
        lines.append(f"  Accuracy: {accuracy}")
        lines.append(f"  Agentes mas activos: {', '.join(top) if top else 'n/d'}")
        if tp > 0:
            lines.append(f"  Training pairs nuevas: {tp}")
        lines.append("")
    return subject, "\n".join(lines)
