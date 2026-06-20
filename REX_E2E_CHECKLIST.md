# REX · E2E en cuenta descartable — CHECKLIST (NO ejecutar sin GO)

> **DEBT-098 F1 · paso APARTE.** Este E2E **enciende la publicación real de REX** sobre una
> red social. Se ejecuta SOLO con GO explícito del owner. Patrón TikTok (19 jun): cuenta
> throwaway, última puerta antes del disparo irreversible, GO manual, teardown manual.
> Al terminar, prod vuelve a **inerte** (`REX_LIVE_ENABLED` sin setear).

**Estado de partida (verificado 20 jun):** REX desplegado (`7331476`) · `00069` aplicada ·
`REX_LIVE_ENABLED` sin setear (shadow) · universo addon+toggle = 0 · `rex_publish_log` vacío.

---

## Principio de seguridad (igual que TikTok)
- Cuenta de red **DESCARTABLE** (throwaway), NUNCA una de cliente real.
- Cliente de prueba **DESCARTABLE** en la DB, NUNCA un `client_id` productivo.
- Publicar es **IRREVERSIBLE** (algunas redes no borran por API). El post se borra **MANUAL**.
- El flag se enciende SOLO para el test y se apaga al terminar.

---

## PASO 0 · Setup (datos de prueba · todo descartable)
- [ ] Crear/elegir **cliente de prueba descartable** `TEST_CLIENT_ID` (no productivo).
- [ ] Conectar un **perfil Zernio descartable** + mapear su cuenta a `TEST_CLIENT_ID`
      (`social_accounts.zernio_account_id` = la cuenta **throwaway**, platform p.ej. `facebook`).
- [ ] Insertar **1 `scheduled_post`** del `TEST_CLIENT_ID`: `status='pending'`,
      `scheduled_for` en el **pasado** (`now()-1h`), `content_id` de un draft con
      `confidence>=7` y `brand_voice_score>=0.7`, `media_url` presente si la red la exige.
- [ ] En `clients`, para `TEST_CLIENT_ID`: `rex_addon_active=true`, `autonomous_mode_on=true`,
      `crisis_active=false`.

## PASO 1 · ÚLTIMA PUERTA antes de encender el flag (binding correcto · lección TikTok)
- [ ] **Verificar con datos** que el binding resuelve a la cuenta **DESCARTABLE**, no a una real:
  ```python
  # READ-ONLY · PYTHONPATH=backend venv/Scripts/python.exe
  from app.api.routes.clients_v3._clients_reader import get_zernio_account_id
  acc = get_zernio_account_id("TEST_CLIENT_ID", "facebook")
  print("zernio_account_id resuelto:", acc)   # DEBE ser el de la cuenta throwaway
  ```
- [ ] Confirmar a ojo que `acc` == la cuenta descartable (NO la de ningún cliente real).
      **Si hay cualquier duda del binding → ABORTAR** (no se enciende el flag).

## PASO 2 · Confirmaciones previas al disparo irreversible
- [ ] **⏵⏵ auto-accept OFF** en la sesión (publicar es irreversible · cada acción se aprueba a mano).
- [ ] Confirmar que NINGÚN otro cliente tiene addon+toggle (universo debe ser solo el de prueba):
  ```python
  sb.table("clients").select("id", count="exact").eq("rex_addon_active", True).eq("autonomous_mode_on", True).execute().count
  # Esperado: 1 (solo TEST_CLIENT_ID)
  ```

## PASO 3 · Encender REX_LIVE_ENABLED SOLO para el test
**Recomendado (más controlado · Railway queda inerte):** un script one-shot con el flag en
SU proceso, apuntando a prod, que dispara el worker UNA vez para el cliente de prueba:
```bash
REX_LIVE_ENABLED=true PYTHONPATH=backend venv/Scripts/python.exe -c "
import asyncio
from app.bc_cognition.application.rex_publish_uc import run_rex_for_client
from app.workers.rex_publish_fn import select_publish_fn
print(asyncio.run(run_rex_for_client('TEST_CLIENT_ID', select_publish_fn())))
"
```
- Railway prod **NO** se toca (su env sigue sin `REX_LIVE_ENABLED` → el cron de prod sigue shadow).
- Alternativa (NO recomendada): setear `REX_LIVE_ENABLED=true` en Railway y esperar el cron `*/5`.
  Caveat: pone TODO el cron de prod en live durante la ventana (ok hoy porque solo el test
  está en el universo, pero menos controlado · hay que acordarse de apagarlo).

## PASO 4 · Verificar el publish real (con datos)
- [ ] `rex_publish_log`: 1 fila `gate_result='publish'` · `published_at` **NOT NULL** · `platform`.
- [ ] `scheduled_posts` (el de prueba): `status='published'` + `platform_post_id` real.
- [ ] `agent_memory`: 1 fila `agent_code='rex_publisher'` · `was_correct=NULL` · `aria_nba_id`=content_id.
- [ ] El post aparece en la cuenta **descartable** (verificación visual).

## PASO 5 · Verificar los HOLD (el gate frena lo que debe)
Repetir el disparo (PASO 3) variando UN dato del post/cliente de prueba:
- [ ] Post **sin media** en red que la exige (IG/TikTok) → `rex_publish_log` `gate_result='hold'`
      `hold_reason='no_media'` · `scheduled_posts` sigue `pending`.
- [ ] **4to post del día** (sembrar 3 publish reales antes) → `hold` `daily_limit_reached`.
- [ ] `crisis_active=true` en el cliente → `hold` `crisis_active` (kill-switch · congela TODO).
- [ ] (opcional) `brand_voice_score<0.7` → `hold` `brand_voice_below_bar`.

## PASO 6 · APAGAR + teardown
- [ ] **Apagar `REX_LIVE_ENABLED`** (si se usó la alternativa de Railway · quitar la var).
      Con el método recomendado no hay nada que apagar (el flag vivió solo en el proceso del script).
- [ ] Confirmar prod inerte de nuevo: `rex_publish_log` no crece, universo vuelve a 0 (bajar
      el toggle del cliente de prueba o borrarlo).
- [ ] **Borrar el post publicado MANUALMENTE de la red descartable** (lección TikTok: algunas
      redes no borran por API). Borrar **ANTES** de desconectar la cuenta descartable.
- [ ] Desconectar/limpiar el perfil Zernio descartable y el cliente de prueba.

## PASO 7 · Verificar aislamiento (no se tocó a nadie real)
- [ ] Confirmar que `platform_post_id` salió en la cuenta **descartable** (no en una real).
- [ ] `rex_publish_log` no tiene filas de ningún `client_id` productivo.
- [ ] Ninguna cuenta de cliente real cambió de estado.

---

## Criterio de cierre
E2E EXITOSO = publish real en cuenta descartable + los 3+ holds correctos + aislamiento
confirmado + prod de vuelta inerte (`REX_LIVE_ENABLED` sin setear · universo 0). Recién
entonces se considera la **activación gradual por cliente real** (un cliente que compró +
encendió el toggle, con su propia cuenta · supervisado).

**persona/limits intactos · este doc es el guion · la ejecución espera GO aparte del owner.**
