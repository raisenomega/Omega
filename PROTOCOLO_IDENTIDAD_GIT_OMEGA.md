# PROTOCOLO DE IDENTIDAD GIT — OmegaRaisen
## Versión 2.0 · 17 mayo 2026 · CRÍTICO

> **🚨 LEER COMPLETO ANTES DEL PRIMER COMMIT EN ESTE PROYECTO 🚨**
>
> **Problema que resuelve:** que los commits de OmegaRaisen aparezcan con
> la identidad CORRECTA — la cuenta corporativa **raisenomega**, no con
> ninguna identidad personal.
>
> **Solución:** `includeIf` de Git. Se activa automáticamente al estar
> dentro de la carpeta del proyecto. No requiere comandos manuales por commit.

---

## SECCIÓN 1 — DATOS CANÓNICOS (NO ALTERAR)

```
═════════════════════════════════════════════════════════════════
  IDENTIDAD ÚNICA DE OMEGARAISEN — esta es LA fuente de verdad
═════════════════════════════════════════════════════════════════

  Ruta local en disco       D:\Omega Master redes\
                            (Windows · con espacio · disco D:)

  Cuenta GitHub             raisenomega
  Email GitHub login        raisenagencypr@gmail.com
  Repositorio único         https://github.com/raisenomega/Omega.git

  Git config — user.name    raisenomega
  Git config — user.email   raisenagencypr@gmail.com
  Git config — signingKey   [GPG/SSH corporate por configurar]
═════════════════════════════════════════════════════════════════
```

**Sin excepciones. Sin variantes. Sin identidades alternativas.**

---

## ⚠️ SETUP REAL EN PRODUCCIÓN (descubierto 17 may 2026)

Esta máquina tiene **DOS proyectos distintos de Raisen Agency**. Esta es la realidad:

```
PROYECTO                  RUTA LOCAL                  GITCONFIG FILE
──────────────────────    ──────────────────────────  ──────────────────────────────────
OmegaRaisen (ESTE)        D:\Omega Master redes\      C:\Users\muscl\.gitconfig-omegamaster
                                                        user.name  = raisenomega
                                                        user.email = raisenagencypr@gmail.com

Raisen Omega (LEGACY)     D:\Raisen Omega\            C:\Users\muscl\.gitconfig-raisen
                                                        user.name  = raisenomega
                                                        user.email = 283876472+raisenomega@users.noreply.github.com
```

**`~/.gitconfig` global tiene DOS bloques includeIf:**

```ini
[includeIf "gitdir:D:/Raisen Omega/"]
  path = C:/Users/muscl/.gitconfig-raisen

[includeIf "gitdir:D:/Omega Master redes/"]
  path = C:/Users/muscl/.gitconfig-omegamaster
```

**REGLA:** NO modificar `.gitconfig-raisen` — es del proyecto legacy y no te incumbe.
**REGLA:** Para OmegaRaisen, SIEMPRE usar `.gitconfig-omegamaster`.

---

## SECCIÓN 2 — SETUP PASO A PASO (WINDOWS / GIT BASH)

### 2.1 — Verifica dónde estás

```bash
cd "D:/Omega Master redes"
pwd
# Esperado: /d/Omega Master redes (en Git Bash)
```

Si no estás ahí, **detente**. El protocolo asume que esa es tu ruta.
Si tu ruta es distinta: corrige antes de continuar — la configuración
debe matchear exactamente.

### 2.2 — Verifica tu identidad git actual

```bash
git config --get user.email
git config --get user.name
```

Si retorna `raisenagencypr@gmail.com` y `raisenomega`: ya está bien.
Si retorna cualquier otra cosa: continúa con el setup.

### 2.3 — Crea el archivo de configuración corporativa

Crea **`C:\Users\muscl\.gitconfig-omegamaster`** con este contenido exacto:

```ini
[user]
  name = raisenomega
  email = raisenagencypr@gmail.com
  # signingKey = <GPG/SSH key fingerprint cuando se configure>

[commit]
  # gpgsign = true                 # descomentar cuando configures GPG corp

[init]
  defaultBranch = main

[core]
  autocrlf = input                  # consistencia LF entre Win/Linux
  ignorecase = false                # importante para Linux deploys
```

### 2.4 — Activa includeIf en tu `.gitconfig` global

Edita **`C:\Users\muscl\.gitconfig`** (tu config global de Git) y **agrega al final**:

```ini
[includeIf "gitdir:D:/Omega Master redes/"]
  path = C:/Users/muscl/.gitconfig-omegamaster
```

**Tres detalles críticos:**

1. **La ruta en `gitdir:` termina con `/`** — es directorio, no archivo
2. **Usa forward slashes `/` aunque sea Windows** — Git lo prefiere así
3. **Match es case-insensitive en Windows** — pero el path debe existir tal cual

### 2.5 — Verifica que funciona

```bash
# Dentro del proyecto: identidad CORPORATIVA
cd "D:/Omega Master redes"
git config --get user.email
# Esperado:  raisenagencypr@gmail.com
git config --get user.name
# Esperado:  raisenomega

# Fuera del proyecto: tu identidad personal (la que tengas global)
cd ~
git config --get user.email
# (lo que sea que tengas como default global, NO debe ser raisenagencypr@...)
```

**Si dentro del proyecto NO retorna `raisenagencypr@gmail.com`:**
- Verifica que la sección `[includeIf]` está al **final** del `.gitconfig`
- Verifica que la ruta termina con `/`
- Verifica que `.gitconfig-omegamaster` existe y tiene los valores correctos
- Ejecuta `git config --list --show-origin | grep user` para ver de dónde viene la identidad

---

## SECCIÓN 3 — CONFIGURACIÓN MULTIPLATAFORMA

Si trabajas también desde Linux/Mac, agrega ambas variantes:

En `~/.gitconfig`:

```ini
[includeIf "gitdir:D:/Omega Master redes/"]
  path = ~/.gitconfig-omegamaster

[includeIf "gitdir:~/repos/Omega Master redes/"]
  path = ~/.gitconfig-omegamaster

# Si clonas con otro nombre de carpeta, agrega otra entrada
```

Y `~/.gitconfig-omegamaster`:

```ini
[user]
  name = raisenomega
  email = raisenagencypr@gmail.com
```

---

## SECCIÓN 4 — CLONAR EL REPOSITORIO

Al clonar el repo nuevo, **clona dentro de `D:\`** para que el `includeIf`
matchee la ruta esperada:

```bash
cd D:/
git clone https://github.com/raisenomega/Omega.git "Omega Master redes"
cd "Omega Master redes"

# Verificación inmediata:
git config --get user.email
# DEBE retornar: raisenagencypr@gmail.com
```

Si usas **SSH con clave separada** para la cuenta corporativa:

`~/.ssh/config`:
```
Host github.com-raisenomega
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_raisenomega
  IdentitiesOnly yes
```

Y clonas con:
```bash
cd D:/
git clone git@github.com-raisenomega:raisenomega/Omega.git "Omega Master redes"
```

---

## SECCIÓN 5 — VERIFICACIÓN PRE-PUSH AUTOMATIZADA

`scripts/validate-before-push.sh` debe incluir como **Check 0** (primero,
antes de cualquier otro):

```bash
# ─── Check 0: identidad git correcta ───
USER_EMAIL=$(git config --get user.email)
USER_NAME=$(git config --get user.name)
EXPECTED_EMAIL="raisenagencypr@gmail.com"
EXPECTED_NAME="raisenomega"

if [ "$USER_EMAIL" != "$EXPECTED_EMAIL" ] || [ "$USER_NAME" != "$EXPECTED_NAME" ]; then
  echo "❌ IDENTIDAD GIT INCORRECTA"
  echo "   user.name actual:    $USER_NAME      (esperado: $EXPECTED_NAME)"
  echo "   user.email actual:   $USER_EMAIL     (esperado: $EXPECTED_EMAIL)"
  echo ""
  echo "   Setup: ver PROTOCOLO_IDENTIDAD_GIT_OMEGA.md Sección 2"
  exit 1
fi
echo "✓ Identidad git: $USER_NAME <$USER_EMAIL>"
```

Sin este check verde: **push bloqueado**. Sin negociación.

---

## SECCIÓN 6 — TROUBLESHOOTING

### "Mis commits siguen apareciendo con otra identidad"

1. Verifica `git config --get user.email` **dentro de la carpeta del proyecto**
2. Si retorna lo correcto pero los commits no: re-firma con
   ```bash
   git commit --amend --reset-author --no-edit
   ```
3. Si retorna lo incorrecto: revisa orden del includeIf en `.gitconfig`
   (las directivas posteriores ganan sobre las anteriores)

### "El includeIf no se activa"

- La sección `[includeIf ...]` debe estar **al final** del `.gitconfig` global
- El `gitdir:` debe terminar con `/`
- La ruta debe matchear exactamente (Windows es case-insensitive, Linux/Mac no)
- Verifica con:
  ```bash
  git config --list --show-origin | grep user
  # Te dice qué archivo está aportando user.name y user.email
  ```

### "Quiero usar GPG corporate signing"

1. Genera key GPG asociada al email corporativo:
   ```bash
   gpg --full-generate-key
   # Email a usar: raisenagencypr@gmail.com
   ```
2. Lista keys:
   ```bash
   gpg --list-secret-keys --keyid-format=long
   # Copia el ID después de "sec   ed25519/<KEY_ID>"
   ```
3. Añade el `<KEY_ID>` a `~/.gitconfig-omegamaster`:
   ```ini
   [user]
     signingKey = <KEY_ID>
   [commit]
     gpgsign = true
   ```
4. Exporta la public key y agrégala en GitHub bajo la cuenta `raisenomega`:
   ```bash
   gpg --armor --export <KEY_ID>
   # Copia el output completo → GitHub Settings → SSH and GPG keys → New GPG key
   ```

### "Tengo identidad mixta en commits viejos"

Si encuentras commits ya hechos con identidad equivocada, **antes de push**:

```bash
# Rebase interactivo desde el commit problemático
git rebase -i <hash-del-commit-anterior>
# Marca como "edit" cada commit afectado
# Por cada commit pausado:
git commit --amend --reset-author --no-edit
git rebase --continue
```

Si los commits ya están en remoto: **no reescribas historia pública**.
Documenta el incidente en `SOURCE_OF_TRUTH.md` como deuda DEBT-XXX y
sigue adelante con identidad correcta desde ese punto.

---

## SECCIÓN 7 — REGLAS DE OPERACIÓN INVIOLABLES

```
R1   NUNCA ejecutar `git config --global user.email raisenagencypr@gmail.com`
     Eso pone la identidad CORP como default GLOBAL — todo proyecto
     personal heredaría esa identidad. Usa SIEMPRE includeIf por path.

R2   ANTES de cada commit en OmegaRaisen: verificar identidad
       git config --get user.email
     Debe retornar:  raisenagencypr@gmail.com

R3   El pre-push hook (validate-before-push.sh) ejecuta Check 0 antes de
     todo. No usar --no-verify excepto en emergencia documentada con
     aprobación del owner en el commit message.

R4   La cuenta GitHub `raisenomega` es la única que existe para este
     repo. La cuenta de login es `raisenagencypr@gmail.com`. Cualquier
     intento de operar con otra cuenta = error crítico.

R5   Cualquier identidad git que NO sea exactamente:
        user.name  = raisenomega
        user.email = raisenagencypr@gmail.com
     dentro de D:\Omega Master redes\ es VIOLACIÓN del protocolo.
     Push bloqueado por hook.
```

---

## SECCIÓN 8 — VERIFICACIÓN PERIÓDICA

**Después de cada push**, mira el commit en GitHub web UI:
- Author debe aparecer como **raisenomega**
- Avatar debe ser el de la cuenta corporativa
- Click en el author debe ir a `github.com/raisenomega`

**Mensualmente**, audita los últimos commits:

```bash
cd "D:/Omega Master redes"
git log --pretty=format:"%h %an <%ae> %s" -30

# Esperado: TODOS los commits deben ser:
#   <hash> raisenomega <raisenagencypr@gmail.com> <descripción>
```

Si encuentras commits con autor distinto en historia reciente:
1. Documenta en `SOURCE_OF_TRUTH.md` como incidente
2. Investiga causa (¿alguien clonó fuera de `D:\Omega Master redes\`?)
3. Refuerza el setup en máquinas afectadas
4. Considera firmar commits con GPG para autenticar identidad criptográficamente

---

## SECCIÓN 9 — INTEGRACIÓN CON CLAUDE CODE

`CLAUDE.md` referencia este protocolo. Cualquier sesión de Claude Code en
este repo debe verificar identidad git como parte del bootstrap.

`.claude/skills/iniciar-fase/SKILL.md` exige:
```bash
git config --get user.email
# Si NO retorna raisenagencypr@gmail.com → DETENTE y avisa al owner
```

`.claude/hooks/verify-on-stop.sh` también verifica esto antes de cerrar
una sesión con commits pendientes.

---

## SECCIÓN 10 — CHECKLIST AL PRIMER USO

```
[ ] Estoy físicamente en D:\Omega Master redes\
[ ] Existe C:\Users\muscl\.gitconfig-omegamaster con los valores correctos
[ ] Existe sección [includeIf "gitdir:D:/Omega Master redes/"] al final
    de C:\Users\muscl\.gitconfig
[ ] git config --get user.email retorna raisenagencypr@gmail.com
[ ] git config --get user.name retorna raisenomega
[ ] git remote -v apunta a https://github.com/raisenomega/Omega.git
[ ] scripts/validate-before-push.sh incluye Check 0 (identidad)
[ ] El primer commit de prueba aparece en GitHub con autor raisenomega
```

Sin estos 8 ítems verde: **no commiteo nada todavía**.

---

```
PROTOCOLO_IDENTIDAD_GIT_OMEGA.md
Versión 2.0 · 17 mayo 2026
Próxima revisión: al configurar GPG corporate signing
Compatible con: IDENTIDAD_GIT_CRITICA.md + CLAUDE.md sección Identidad
```
