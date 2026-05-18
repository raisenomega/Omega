---
name: cerrar-ciclo
description: |
  Procedimiento para cerrar una fase de desarrollo: tests, validación,
  registro de aprendizaje, commit, push.
---

# Skill: cerrar-ciclo — OmegaRaisen

Usa esta skill al **terminar una fase iniciada con `iniciar-fase`**.

## Procedimiento

### 1. Verificación local

```bash
# 1.1 Tests pasando
npm test
cd backend && pytest && cd ..

# 1.2 Typecheck
npx tsc --noEmit

# 1.3 Validación completa (9 checks)
bash scripts/validate-before-push.sh

# 1.4 SHA1 guardrails (si modificaste limits_omega.py)
bash scripts/verify-guardrails.sh
```

Si CUALQUIERA falla: arregla antes de continuar. No commitear con rojo.

### 2. Registro de aprendizaje

Invoca `memory-writer` con el resumen de la fase:

```
agent_code:    [feature_o_fix_code]
memory_type:   procedural
context:       "Fase X — descripción"
decision:      "Aproximación elegida"
reasoning:     "Por qué esta sobre alternativas"
confidence:    [0-10]
metadata:      {"files_changed": N, "tests_added": M, "time_invested_min": T}
```

### 3. Si hay deuda nueva detectada

Invoca skill `registrar-deuda`. NO cierres fase con deuda silenciosa.

### 4. Commit

Convencional commits:

```
<scope>(<area>): <descripción concisa>

- Detalle 1
- Detalle 2
- Detalle 3

Refs: #issue (si aplica)
Tests: [agregados / pasando]
DDD: [reglas relevantes verificadas]
```

Scope ejemplos: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `migration`.
Area ejemplos: `bc-cognition`, `bc-content-lab`, `auth`, `billing`, `agents`.

### 5. Push

```bash
git push origin <branch>
```

El pre-push hook ejecuta `validate-before-push.sh` automáticamente.

### 6. Resumen al humano

Reporta en mensaje:

```markdown
## Fase cerrada: [nombre]

### Completado
- [item 1]
- [item 2]

### NO completado (re-scope o deferred)
- [item con razón]

### Métricas
- Archivos modificados: N
- Líneas añadidas / eliminadas: +X / -Y
- Tests añadidos: M
- Tiempo invertido: T

### Validación
- validate-before-push.sh: ✓ 9/9
- Tests: ✓ X/X passing
- SHA1 guardrails: [intacto / rotado con baseline nuevo]

### Deuda registrada
- [DEBT-XXX si aplica]

### Próximos pasos
[Sugerencia para siguiente sesión]
```

## Cuándo NO cerrar

- Tests rojos
- validate-before-push.sh falla
- SHA1 rotado sin baseline actualizado
- Hay deuda detectada sin registrar
- Cambiaste scope sin avisar al humano

En esos casos: **mantén la fase abierta, reporta el estado, espera dirección.**

🐢💎 Cerrar mal una fase es peor que dejarla abierta.
