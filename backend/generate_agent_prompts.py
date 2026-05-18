"""
generate_agent_prompts.py
Genera system prompts para los 53 agentes OMEGA sin prompt.
Filosofía: No velocity, only precision 🐢💎

Uso:
  python generate_agent_prompts.py --dry-run   ← solo genera, no inserta
  python generate_agent_prompts.py --insert    ← genera + inserta en Supabase
"""
import os
import sys
import json
import time
import argparse
import anthropic
from supabase import create_client

# ── CONFIG ────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL")
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL env var required")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── CONTEXTO OMEGA ────────────────────────────────────────────────────────────
OMEGA_CONTEXT = """
OMEGA es una plataforma SaaS multi-agente de marketing AI enterprise para Puerto Rico
y Latinoamérica. Tiene 57 agentes especializados en 9 departamentos:

- marketing: agentes de contenido, estrategia, campañas, redes sociales
- security: agentes de monitoreo, compliance, auditoría, protección
- finance: agentes de finanzas, reportes, deuda, facturación
- operations: agentes de operaciones, automatización, flujos internos
- community: agentes de comunidad, engagement, construcción, bienes raíces
- people: agentes de RRHH, reclutamiento, capacitación, cultura
- futures: agentes de inteligencia futura, tendencias, oportunidades
- tech: agentes de arquitectura, código, infraestructura, diseño
- ceo: agente ejecutivo principal

Cada agente:
- Tiene un cliente específico (multi-tenant, client_id en cada query)
- Opera bajo filosofía "No velocity, only precision 🐢💎"
- Responde siempre en español (Puerto Rico)
- Es profesional, preciso, accionable
- NUNCA expone datos de otros clientes
- NUNCA actúa fuera de su scope declarado
"""

# ── AGENTES A GENERAR ─────────────────────────────────────────────────────────
AGENTS_FALTA = [
    # community
    ("CONSTRUCT", "community"), ("ESTATE", "community"), ("HAVEN", "community"),
    ("KIRA", "community"), ("NURTURE", "community"), ("REVIEW", "community"),
    # finance
    ("GUARD", "finance"), ("LEDGER_FIN", "finance"), ("REPORT", "finance"),
    ("SCOPE", "finance"), ("VERA", "finance"),
    # futures
    ("MIRROR_FUT", "futures"), ("NEXUS", "futures"), ("ORACLE", "futures"),
    ("SCOUT", "futures"), ("VEGA", "futures"),
    # marketing
    ("DANI", "marketing"), ("DUDA", "marketing"), ("LOLA", "marketing"),
    ("LUAN", "marketing"), ("MALU", "marketing"), ("MAYA", "marketing"),
    ("SARA", "marketing"),
    # operations
    ("ANCHOR", "operations"), ("ECHO", "operations"), ("MIRROR_OPS", "operations"),
    ("ONYX", "operations"), ("RESELL_OPS", "operations"), ("REX", "operations"),
    # people
    ("LEDGER_HR", "people"), ("PROMETHEUS", "people"), ("PULSE", "people"),
    ("RECRUIT", "people"), ("SOPHIA", "people"), ("TRAINER", "people"),
    # security
    ("ARCH_SCAN", "security"), ("AUTO_HEALER", "security"), ("COMPLIANCE", "security"),
    ("DB_GUARDIAN", "security"), ("DEBT_HUNTER", "security"), ("DEP_WATCH", "security"),
    ("FORTRESS", "security"), ("MIGRATION_VAL", "security"), ("PULSE_MON", "security"),
    ("SENT_BRAIN", "security"), ("SPEED_ANZ", "security"), ("VAULT", "security"),
    # tech
    ("ARCH", "tech"), ("LUNA", "tech"), ("PIXEL", "tech"),
    ("PULSE_TECH", "tech"), ("SCRIBE", "tech"), ("SHIELD", "tech"),
]


def generate_prompt(client: anthropic.Anthropic, agent_code: str, department: str) -> str:
    """Genera un system prompt para un agente usando Claude"""
    user_msg = f"""Genera un system prompt para el agente OMEGA con estos datos:

Agent Code: {agent_code}
Department: {department}

Contexto de OMEGA:
{OMEGA_CONTEXT}

Reglas para el system prompt:
1. Entre 150-300 palabras
2. Define claramente el ROL y RESPONSABILIDADES del agente
3. Define el SCOPE — qué hace y qué NO hace
4. Incluye instrucciones de seguridad: siempre usar client_id, nunca exponer datos de otros clientes
5. Tono: profesional, preciso, ejecutivo
6. Idioma: español (Puerto Rico)
7. Termina con: "Filosofía: No velocity, only precision 🐢💎"

Responde SOLO con el system prompt, sin explicaciones adicionales, sin comillas."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=600,
        messages=[{"role": "user", "content": user_msg}]
    )
    return response.content[0].text.strip()


def run(dry_run: bool):
    """Función principal"""
    print(f"\n🚀 OMEGA Agent Prompt Generator")
    print(f"   Modo: {'DRY RUN (sin insertar)' if dry_run else 'INSERT en Supabase'}")
    print(f"   Agentes a procesar: {len(AGENTS_FALTA)}\n")

    if not ANTHROPIC_KEY:
        print("❌ ERROR: ANTHROPIC_API_KEY no configurada")
        sys.exit(1)

    if not dry_run and not SUPABASE_KEY:
        print("❌ ERROR: SUPABASE_SERVICE_KEY no configurada")
        sys.exit(1)

    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if not dry_run else None

    results = []
    errors = []

    for i, (agent_code, department) in enumerate(AGENTS_FALTA, 1):
        print(f"[{i:02d}/{len(AGENTS_FALTA)}] Generando {agent_code} ({department})...", end=" ")

        try:
            prompt = generate_prompt(anthropic_client, agent_code, department)

            if not dry_run and supabase:
                supabase.table("omega_agents") \
                    .update({"system_prompt": prompt}) \
                    .eq("agent_code", agent_code) \
                    .execute()
                print("✅ INSERTADO")
            else:
                print("✅ GENERADO")

            results.append({
                "agent_code": agent_code,
                "department": department,
                "prompt": prompt,
                "status": "ok"
            })

            time.sleep(0.5)  # Rate limit cortesía

        except Exception as e:
            print(f"❌ ERROR: {e}")
            errors.append({"agent_code": agent_code, "error": str(e)})

    # ── REPORTE FINAL ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"REPORTE FINAL")
    print(f"{'='*60}")
    print(f"  ✅ Exitosos: {len(results)}")
    print(f"  ❌ Errores:  {len(errors)}")

    if errors:
        print(f"\n  Agentes con error:")
        for e in errors:
            print(f"    - {e['agent_code']}: {e['error']}")

    # Guarda resultados en JSON para revisión
    output_file = "generated_prompts.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n  📄 Prompts guardados en: {output_file}")
    print(f"\n🐢💎 Completado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OMEGA Agent Prompt Generator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Genera sin insertar")
    group.add_argument("--insert", action="store_true", help="Genera e inserta en Supabase")
    args = parser.parse_args()

    run(dry_run=args.dry_run)
