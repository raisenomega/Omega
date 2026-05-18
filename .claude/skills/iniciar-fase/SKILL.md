---
name: iniciar-fase
description: |
  Procedimiento para iniciar una fase de desarrollo (feature, refactor, fix).
  Carga contexto, verifica precondiciones, declara intención antes de tocar código.
---

# Skill: iniciar-fase — OmegaRaisen

Usa esta skill **al inicio de cualquier sesión de trabajo significativa**:
nuevo feature, refactor, fix de issue, integración, migration.

## Procedimiento

### 1. Lectura obligatoria

Lee, en este orden estricto:
1. **`INDICE_PROYECTO.md`** — mapa maestro · te dice qué leer según tu scope
2. **`IDENTIDAD_GIT_CRITICA.md`** §2 — verifica las 4 condiciones git
3. **`CLAUDE.md`** — constitución 60L con reglas non-negotiable
4. **`SOURCE_OF_TRUTH.md`** — qué existe, qué no, las 11 deudas vigentes
5. **Tier 2 según scope** (de `INDICE_PROYECTO.md` §2):
   - Arquitectura/agentes  → `DDD_REGLAS_OMEGA.md` + `BC_COGNITION_OMEGA.md`
   - MCPs/integraciones    → `MCP_ARSENAL_OMEGA.md`
   - Deploy/migración      → `MIGRATION_PLAN_OMEGA.md`
   - Seguridad/auth/RLS    → `PROTOCOLO_SEGURIDAD_OMEGA.md`
   - Identidad git         → `PROTOCOLO_IDENTIDAD_GIT_OMEGA.md`
   - Base de datos         → `supabase/migrations/00001-00003.sql`
6. `graphify-out/GRAPH_REPORT.md` si existe
7. Últimos 5 episodios de `agent_memory` filtrados por el agente/feature relevante

### 2. Verificación de precondiciones

Ejecuta:
```bash
bash scripts/verify-guardrails.sh     # SHA1 limits intacto
git status                            # ramas limpias, en main actualizado
git config user.email                 # debe ser raisenagencypr@gmail.com
```

### 3. Declaración de intención

Escribe en un mensaje al humano (sin tocar código aún):

```markdown
## Fase: [nombre]

### Scope
[Qué voy a hacer · qué NO voy a hacer]

### Archivos esperados
- A crear: [lista]
- A modificar: [lista con razón]
- A NO tocar: [lista]

### Reglas DDD aplicables
[R-XX-001, R-YY-002, ...]

### Riesgos
[Qué podría salir mal · cómo lo detecto]

### Criterio de éxito
[Qué tiene que ser cierto al cerrar]

### Aprobación requerida
[ ] Plan Mode? (si ≥3 archivos)
[ ] Owner approval? (si toca limits_omega.py, hooks, settings, migrations)
```

Espera respuesta del humano antes de empezar.

### 4. Trabajar en plan

- **Un cambio por commit** — atómico
- **Tests primero** cuando aplique
- **Cada decisión significativa**: invocar memory-writer
- **Si encontrás algo inesperado**: pausar, reportar, esperar dirección

### 5. Cerrar con cerrar-ciclo

Cuando completes la fase, ejecuta la skill `cerrar-ciclo`.

## Anti-patrones a evitar

❌ Empezar a editar código sin haber leído los documentos
❌ "Lo entiendo desde el código" — el contexto vive en los .md
❌ Pasar directo de "tengo idea" a `Write` sin declarar intención
❌ Cambiar scope a mitad de fase ("ya que estoy aquí…")
❌ Asumir que el humano sabe lo que vas a hacer

🐢💎 La precisión empieza antes de la primera línea de código.
