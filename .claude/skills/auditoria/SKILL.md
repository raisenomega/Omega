---
name: auditoria
description: |
  Lanza una auditoría completa sobre un scope (un bounded context, un agente,
  toda la app). Usa el subagente `auditor` (Opus, read-only).
---

# Skill: auditoria — OmegaRaisen

Usa esta skill cuando necesitas **diagnóstico profundo sin riesgo de modificación**.

## Cuándo usarla

- Antes de un refactor grande (qué tan mal estamos vs DDD)
- Después de un periodo de desarrollo rápido (¿se acumuló deuda?)
- Como parte de cierre de fase mayor
- Sospecha de drift (algo funciona raro pero no sé qué)
- Compliance check (auditoría externa, certificación)

## Scopes posibles

```
GLOBAL                  Toda la app
BACKEND                 Solo backend/app/
FRONTEND                Solo src/
BC <nombre>             Un bounded context (ej: bc-02-content-lab)
COGNITION               Solo bc-cognition/
AGENTE <code>           Un agente específico (ej: agente=content_creator)
REGLA <id>              Una regla específica (ej: regla=I1)
SEGURIDAD               Solo categoría G + secretos + RLS
```

## Procedimiento

### 1. Definir scope

```markdown
SCOPE: [uno de arriba]
PROFUNDIDAD: [shallow | normal | deep]
FORMATO: [markdown | json | issue]
```

### 2. Invocar auditor

Llama al subagente `auditor` con el scope. Recibirás un reporte estructurado
con hallazgos clasificados por severidad.

### 3. Revisión del reporte

El reporte llega con esta estructura (ver `.claude/agents/auditor.md`):

- 🔴 CRÍTICA: bloquea push
- 🟠 ALTA: corregir en sprint actual
- 🟡 MEDIA: code review
- 🟢 BAJA: registrar como mejora futura

### 4. Decisión

Para cada hallazgo:

| Severidad | Acción |
|-----------|--------|
| 🔴 | Pausar features, abrir fase de fix inmediata |
| 🟠 | Crear issue, priorizar para siguiente sprint |
| 🟡 | Discutir en próxima review semanal |
| 🟢 | Agregar a backlog de mejoras |

### 5. Si hay hallazgos críticos

**No procedas con desarrollo nuevo hasta corregir.**

Abre fase con `iniciar-fase` específica para arreglar lo crítico.
Esto es regla X1 (SENTINEL ≥ 95): el sistema no avanza con criticidad pendiente.

### 6. Registrar la auditoría

```sql
INSERT INTO agent_memory (
  agent_code, memory_type, context, decision, reasoning, confidence, metadata
) VALUES (
  'auditor',
  'episodic',
  'Auditoría [scope] · [fecha]',
  'N hallazgos: X críticos, Y altos, Z medios',
  'Reporte completo en [path]',
  10,  -- auditor read-only: confidence siempre máxima sobre lo observado
  jsonb_build_object('scope', '[scope]', 'critical_count', X, 'high_count', Y)
);
```

## Anti-patrones

❌ Auditar para "verse bien" sin intención de actuar sobre hallazgos
❌ Auditar e ignorar 🟠 críticos
❌ Auditar sin scope claro (resultados ruidosos)
❌ Pedir auditor que también corrija (es read-only por diseño)
❌ Auditar el mismo scope dos veces seguidas sin cambios entre medio

🐢💎 La auditoría que no se actúa es teatro de proceso.
