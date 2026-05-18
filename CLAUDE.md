# OmegaRaisen — CLAUDE.md

## 🗺️ ENTRADA AL PROYECTO

**Antes de leer este archivo, lee `INDICE_PROYECTO.md`** — es el mapa maestro
con orden de lectura, mapa de archivos, y gates de readiness. Este `CLAUDE.md`
es Tier 1 #3 en ese orden (después del INDICE y de IDENTIDAD_GIT_CRITICA).

## 🚨 IDENTIDAD GIT — VERIFICACIÓN BLOQUEANTE (antes de cualquier otra cosa)

```
RUTA LOCAL      D:\Omega Master redes\
REPO            https://github.com/raisenomega/Omega.git
user.name       raisenomega
user.email      raisenagencypr@gmail.com
```

Antes de tocar git, ejecuto las 4 verificaciones de `IDENTIDAD_GIT_CRITICA.md`
Sección 2. Si CUALQUIERA falla → me detengo y reporto al owner.
**No hay "git rápido"** — la identidad se verifica siempre.

## Comandos esenciales
Build front:  `npm run build`
Dev front:    `npm run dev`
Test front:   `npm test` (vitest)
Types front:  `npx tsc --noEmit`
Dev back:     `cd backend && uvicorn app.main:app --reload`
Test back:    `cd backend && pytest`
Eval:         `npx promptfoo eval`
Validate:     `bash scripts/validate-before-push.sh`

## Reglas NON-NEGOTIABLE
- Solo **Anthropic** para texto/razonamiento. Excepción: **Nano Banana** (imagen) + **Veo 3.1** (video) bajo `bc_cognition/infrastructure/`
- Cero `any` en TypeScript. Cero `@ts-ignore`. Cero `Any` en Python.
- Archivos ≤75 líneas (warning) · >100 líneas bloquea push (excepción: `shadcn/ui`, `supabase/types.ts`, `limits_omega.py`)
- `bc_cognition/domain/` no importa nada externo
- SHA1 de `limits_omega.py` intacto — el hook lo verifica
- Cero secretos hardcoded — el hook escanea con regex
- Un cambio por fase — no mezclar scopes (Plan Mode obligatorio si ≥3 archivos)
- RLS activa en TODA tabla con `user_id`, `client_id`, `org_id`, `reseller_id`

## Protocolo de inicio de sesión
1. Lee `INDICE_PROYECTO.md` (mapa maestro · orden completo)
2. Verifica identidad git (4 condiciones de `IDENTIDAD_GIT_CRITICA.md` §2)
3. Lee `SOURCE_OF_TRUTH.md` (lo que existe, lo que no, deudas, métrica)
4. Lee Tier 2 según scope (`INDICE_PROYECTO.md` §2)
5. Lee últimos 5 episodios de `agent_memory` vía Supabase MCP
6. Declara intención al owner · espera confirmación antes de editar

## Routing de modelos
- **Haiku 4.5** (`claude-haiku-4-5-20251001`): clasificación, hashtag-gen, emoji-suggest, summary
- **Sonnet 4.6** (`claude-sonnet-4-6`): content-creator, strategy, brand-voice, analytics — default
- **Opus 4.7** (`claude-opus-4-7`): orchestrator, crisis-manager, oracle-brief, audit — decisiones críticas

## Lo que NUNCA modificas sin aprobación explícita del CEO
- `backend/app/bc_cognition/domain/limits_omega.py` (guardrails — requiere test que falla primero)
- `supabase/migrations/` (versionado inmutable — solo nuevas migraciones)
- `.claude/hooks/` (enforcement determinístico)
- `scripts/guardrails-sha1.txt` (baseline de integridad)
- Reglas en `DDD_REGLAS_OMEGA.md` (contrato del proyecto)
- Datos canónicos de identidad en `IDENTIDAD_GIT_CRITICA.md`
- Mapa de lectura en `INDICE_PROYECTO.md` (orden de tier · gates)

## El principio madre
🐢💎 No velocity, only precision.

Si tu próxima acción incumple una regla de arriba, **detente y pregunta**.
Las reglas existen específicamente para los momentos donde querrías saltártelas.
