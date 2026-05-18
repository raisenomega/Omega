---
name: registrar-deuda
description: |
  Procedimiento para registrar deuda técnica de forma honesta en SOURCE_OF_TRUTH.md.
  Cumple regla P5: aprendizaje honesto, errores se registran con detalle.
---

# Skill: registrar-deuda — OmegaRaisen

Usa esta skill cuando **detectes deuda técnica nueva** o **identifiques una
existente que no estaba documentada**.

## Qué cuenta como deuda

- ✓ Workaround temporal que quedó (TODO_REMOVE, FIX_ME)
- ✓ Test faltante para una función crítica
- ✓ Función >75L que merecería refactor
- ✓ Hardcoded value que debería estar en config
- ✓ Lógica duplicada en N archivos
- ✓ API consumida sin tipos del backend
- ✓ Migration sin RLS donde corresponde
- ✓ Agente sin tests vs evals
- ✓ Datos sintéticos en UI (DEBT-002 actual)

## Qué NO es deuda (es feature/bug)

- ❌ Feature nueva que no existe (es scope, no deuda)
- ❌ Bug que causa fallo (es bug, abrir issue)
- ❌ Discrepancia entre docs y código (es inconsistencia, arreglar)

## Procedimiento

### 1. Verificar que no esté ya registrada

```bash
grep -i "<keyword>" SOURCE_OF_TRUTH.md
```

Si ya existe: agregar nota al item existente, no crear duplicado.

### 2. Calcular ID

Siguiente DEBT-NNN incremental. Ej: si último es DEBT-011, nuevo es DEBT-012.

### 3. Rellenar template

```markdown
| DEBT-XXX | [descripción corta] | [por qué existe] | [tiempo h] | [impacto] |
```

Campos:
- **Descripción corta**: ≤10 palabras, accionable
- **Por qué existe**: razón histórica honesta
  ✓ "Bootstrap inicial Lovable sin tipos compartidos"
  ❌ "No tuvimos tiempo" (vacío)
- **Tiempo estimado**: en horas, conservador (×1.5 tu primera estimación)
- **Impacto**:
  - `Crítico` — viola P1-P5 o regla cero-tolerancia
  - `Alto` — degradación de UX o developer experience medible
  - `Medio` — code review puede flag, pero no bloquea
  - `Bajo` — recomendación, no urgente

### 4. Agregar a `SOURCE_OF_TRUTH.md` sección 6

Editar el archivo, agregar fila en la tabla.

### 5. Recalcular total

Sumar todas las horas, actualizar la línea final:
`**Total deuda estimada: ~XXXh (~Y semanas full-time)**`

### 6. Commit dedicado

```bash
git add SOURCE_OF_TRUTH.md
git commit -m "docs(debt): track DEBT-XXX · <descripción corta>"
```

**Un commit por deuda registrada** — facilita auditoría histórica.

### 7. Si la deuda viola regla DDD

Si es violación de regla DDD activa:
- Hallazgo va también a `auditor` reporte (no oculto)
- Si es crítica (🔴): se pausa desarrollo nuevo hasta arreglar
- Si es alta (🟠): se programa en siguiente sprint

## Anti-patrones

❌ Registrar deuda "para verse responsable" sin intención de arreglar
❌ Marcar como "Bajo" deuda que es Alto/Crítico para parecer menos
❌ Acumular deuda sin tracking (los TODOs sueltos no cuentan)
❌ Estimaciones de tiempo optimistas (×0.5 del real)
❌ Borrar deuda sin commit explícito de resolución

## Cómo se cierra deuda

Cuando arreglas DEBT-XXX:
```bash
git commit -m "fix(debt): resolve DEBT-XXX · <descripción>"
```

Y en el mismo commit: editar SOURCE_OF_TRUTH.md para mover la línea de la tabla
a una nueva tabla "Deuda resuelta" (histórico) o eliminarla (más limpio).

🐢💎 La deuda honesta es mantenible. La invisible es la que mata el proyecto.
