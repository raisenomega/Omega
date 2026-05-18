# 🚨 IDENTIDAD GIT — DOCUMENTO CRÍTICO 🚨
## LECTURA OBLIGATORIA · NO SALTAR · NO INTERPRETAR

> Este documento es **bloqueante**. Cualquier agente (humano o IA) que opere
> sobre el repositorio OmegaRaisen DEBE leerlo y verificar las 4 condiciones
> de la Sección 2 antes de tocar git. Sin verificación: cero commits, cero
> push, cero cambios remotos.
>
> **Por qué este documento existe separado:**
> Errores de identidad git en proyectos corporativos contaminan la atribución,
> rompen la cadena de auditoría, y pueden filtrar identidades personales en
> historial público. Es un error con consecuencias permanentes (rewriting git
> history rara vez es opción aceptable). Por eso este documento es estándar
> aparte — para que sea imposible pasarlo por alto.

---

## 1 — LA VERDAD ÚNICA (memorízala)

```
═════════════════════════════════════════════════════════════════
  IDENTIDAD ÚNICA DE OMEGARAISEN — esta es LA fuente de verdad
═════════════════════════════════════════════════════════════════

  Ruta local en disco       D:\Omega Master redes\
  Repo GitHub               https://github.com/raisenomega/Omega.git
  Cuenta GitHub             raisenomega
  Email GitHub login        raisenagencypr@gmail.com
  Git config — user.name    raisenomega
  Git config — user.email   raisenagencypr@gmail.com

  Archivo gitconfig usado   C:\Users\muscl\.gitconfig-omegamaster
    (≠ .gitconfig-raisen que es del proyecto LEGACY D:/Raisen Omega/)

  SETUP DUAL EN ESTA MÁQUINA:
    D:/Raisen Omega/       → usa .gitconfig-raisen      (NO TOCAR)
    D:/Omega Master redes/ → usa .gitconfig-omegamaster (ESTE proyecto)
═════════════════════════════════════════════════════════════════
```

**Cualquier valor distinto a estos = STOP inmediato.**

---

## 2 — VERIFICACIÓN BLOQUEANTE (correr ANTES de tocar git)

Las 4 condiciones que debes verificar antes de cualquier `git add`, `git commit`,
o `git push`. **TODAS deben ser verdaderas.** Si una falla: detente y reporta.

### Condición 1 — Ubicación física

```bash
pwd
# Esperado:  /d/Omega Master redes   (Git Bash en Windows)
#       o:  D:\Omega Master redes\   (PowerShell / CMD)
```

❌ Si retorna cualquier otra ruta → DETENTE. No estás en el proyecto correcto.

### Condición 2 — user.email del repo

```bash
git config --get user.email
# Esperado:  raisenagencypr@gmail.com
```

❌ Si retorna otra cosa (incluyendo email personal, otro corp, vacío) → DETENTE.
   Lee `PROTOCOLO_IDENTIDAD_GIT_OMEGA.md` Sección 2 para configurar.

### Condición 3 — user.name del repo

```bash
git config --get user.name
# Esperado:  raisenomega
```

❌ Si retorna otra cosa → DETENTE. Misma corrección que condición 2.

### Condición 4 — remote del repo

```bash
git remote -v
# Esperado:  origin  https://github.com/raisenomega/Omega.git (fetch)
#            origin  https://github.com/raisenomega/Omega.git (push)
```

❌ Si retorna otro URL (incluyendo cualquier repo anterior deprecado) → DETENTE.
   No empujes a un repo equivocado.

---

## 3 — ACCIONES SI ALGUNA CONDICIÓN FALLA

### Si user.email o user.name está mal

**No corrijas con `git config --global`.** Eso ensucia tu identidad personal.

La solución es `includeIf` con `.gitconfig-omegamaster`. Pasos:

1. Asegura que existe `C:\Users\muscl\.gitconfig-omegamaster` con:
   ```ini
   [user]
     name = raisenomega
     email = raisenagencypr@gmail.com

   [init]
     defaultBranch = main

   [core]
     autocrlf = input
     ignorecase = false
   ```

2. Asegura que `C:\Users\muscl\.gitconfig` tiene **al final**:
   ```ini
   [includeIf "gitdir:D:/Omega Master redes/"]
     path = C:/Users/muscl/.gitconfig-omegamaster
   ```
   ⚠️ NO tocar la línea `[includeIf "gitdir:D:/Raisen Omega/"]` — ese es el legacy.

3. Verifica que dentro de la carpeta del proyecto, `git config --get user.email`
   ahora retorna el valor correcto.

4. Solo después: procede con git operations.

Ver `PROTOCOLO_IDENTIDAD_GIT_OMEGA.md` para setup completo paso a paso.

### Si la ruta local es incorrecta

Estás en el lugar equivocado. Sal y entra a la ruta correcta:

```bash
cd "D:/Omega Master redes"
```

Si la carpeta no existe, créala clonando:

```bash
cd D:/
git clone https://github.com/raisenomega/Omega.git "Omega Master redes"
cd "Omega Master redes"
```

### Si el remote es incorrecto

```bash
git remote set-url origin https://github.com/raisenomega/Omega.git
git remote -v   # verifica
```

---

## 4 — INTEGRACIÓN AUTOMATIZADA

### Pre-push hook (validate-before-push.sh)

El script `scripts/validate-before-push.sh` incluye como **primer check** la
verificación de identidad. Sin identidad correcta: push bloqueado.

### Stop hook de Claude Code

`.claude/hooks/verify-on-stop.sh` verifica identidad al cerrar cada sesión.

### Skill iniciar-fase

`.claude/skills/iniciar-fase/SKILL.md` exige verificar identidad como parte
del bootstrap de toda sesión.

### CLAUDE.md

`CLAUDE.md` referencia este documento en la sección "Identidad git
(críticamente importante)". Cualquier sesión de Claude Code que comience
sin esta verificación está en violación.

---

## 5 — REGLAS DE COMUNICACIÓN

### Si eres un agente IA

1. **Antes** de ejecutar tu primer comando git: corre las 4 verificaciones
2. Reporta los resultados al usuario antes de hacer `git add`
3. Si CUALQUIER verificación falla: NO procedas. Pide instrucciones.
4. NO asumas que ya está configurado porque "siempre funciona". Verifica
   cada vez.

### Si eres un colaborador humano

1. La primera vez que clonas el repo: corre el setup completo de
   `PROTOCOLO_IDENTIDAD_GIT_OMEGA.md` Sección 2
2. En cada sesión nueva: corre las 4 verificaciones de la Sección 2 de
   este documento
3. Si vas a hacer un commit "rápido" al final del día: igual verifica.
   La velocidad nunca justifica omitir identidad.

---

## 6 — POR QUÉ ESTO IMPORTA

OmegaRaisen es un proyecto corporativo bajo la cuenta `raisenomega`. Los
commits con identidad incorrecta:

1. **Rompen atribución** — el autor "real" del cambio queda mal asociado
2. **Filtran identidad personal** si se usó email personal por error
3. **Confunden auditorías** — quién hizo qué deja de ser verificable
4. **Contaminan estadísticas** del proyecto (contribution graphs, blame)
5. **Pueden romper firmas GPG** si el email no matchea la key

Reescribir historia es posible pero costoso y riesgoso. **La prevención es
infinitamente más barata que la corrección.** Por eso este documento es
estándar separado, no apartado dentro de otro doc.

---

## 7 — REGISTRO DE INCIDENTES

Si encuentras un commit con identidad incorrecta en el historial:

1. **No reescribas historia silenciosamente.** Document primero.
2. Agrega entrada a `SOURCE_OF_TRUTH.md` Sección 6 como `DEBT-XXX`
3. Coordina con el owner cómo proceder:
   - Si el commit NO está en remoto: amend con identidad correcta
   - Si está en remoto y solo en branch personal: rebase + force push
   - Si está en main: documentar y NO reescribir (a menos que owner lo apruebe)

---

## CHECKLIST FINAL DEL DOCUMENTO

Antes de pasar a cualquier otra tarea técnica:

```
[ ] He leído este documento completo
[ ] Sé que la ruta canónica es D:\Omega Master redes\
[ ] Sé que el repo es https://github.com/raisenomega/Omega.git
[ ] Sé que user.email debe ser raisenagencypr@gmail.com
[ ] Sé que user.name debe ser raisenomega
[ ] Sé que las 4 condiciones de la Sección 2 deben verificarse
    antes de cualquier git operation
[ ] Sé qué hacer si alguna condición falla (Sección 3)
[ ] Sé que el pre-push hook bloquea pushes con identidad incorrecta
```

Si los 8 ítems están claros: puedes proceder al trabajo técnico.

🐢💎 La identidad correcta es prerequisito, no decoración.

---

```
IDENTIDAD_GIT_CRITICA.md
Versión 1.0 · 17 mayo 2026
Documento BLOQUEANTE · lectura obligatoria al inicio de cada sesión
Complementa: PROTOCOLO_IDENTIDAD_GIT_OMEGA.md
```
