# PENDIENTES Y PROGRESOS · 25 may 2026

Sesión de fixes de producción (wizard onboarding, Content Lab, ARIA, consola, deploy).
Continuación de la sesión del 24 may. Owner: Ibrain Raisen (CEO) · Cliente piloto: Jorge / La Milagrosa Software.

---

## 1 · Commits de esta sesión (11) · todos en origin/main · gate 10/10 c/u

| Commit | Qué |
|--------|-----|
| `f9fa866` | refactor(calendar): elimina módulo legacy sobre schema fantasma · **cierra DEBT-031** |
| `fc512b9` | docs(sot): cierra DEBT-031 + registra **DEBT-049** (schema fantasma residual NOVA/agent_executions) |
| `7db0fb7` | fix(onboarding): schema zod resiliente en load · data legacy no bloquea save (BUG A v1) |
| `c52a1be` | fix(clients): `list_clients` resuelve reseller desde tabla, no claim JWT (BUG B backend) |
| `d115222` | feat(aria): contexto ampliado del cliente (TAREA C) |
| `ec221ed` | fix(onboarding): wizard persiste social accounts · `username` largo + mapeo a `account_name` |
| `c8973af` | feat(aria): ARIA reporta "Perfil completado X/10" + ✅/❌ por sección |
| `d04f05a` | chore(health): expone `git_sha` en `/health` (verificación de deploy Railway) |
| `68e14b5` | fix(a11y): `DialogTitle` sr-only en overlays sin título (limpia warnings Radix de consola) |
| `c12ef86` | fix(onboarding+clients): wizard % espeja backend + picker prioriza `isOwner` (**AUDIT 1+2**) |
| `b312676` | fix(aria): `_sections` converge con backend+frontend (los 3 calculadores coinciden) |

---

## 2 · Bugs cerrados (causa raíz + fix)

### BUG — Wizard "Editar Cliente" no persistía / mostraba % inflado
Tres causas encadenadas, todas corregidas:
1. **zod estricto bloqueaba el save silenciosamente** (`onInvalid`): data legacy/inválida (hex, uuid, `competitors` legacy `string[]`, enums drift) → `7db0fb7` hace el schema tolerante (`.catch()` + `preprocess`).
2. **`social_accounts.username` `.max(64)` + columna inexistente**: el usuario metía una URL (>64) → zod block; y `username`/`profile_url` **no son columnas** (la real es `account_name`). → `ec221ed`: `.max(500)` front+back + `bulk_insert_social_accounts` mapea `username`→`account_name`, `to_onboarding_payload` lee `account_name`→`username`. (Resto de la app ya usaba `account_name`.)
3. **% del wizard (40%) ≠ % guardado (20%)**: `sectionsFilled` (frontend) tenía falsos positivos por truthiness de arrays vacíos JS (`tone:[]`, `goals.primary_goal:[]` truthy → §3/§4 siempre llenas → blanco ya marcaba 20%). → `c12ef86`: espejo exacto del backend (`.length` + mismos campos). Form en blanco = 0/10 en ambos.

### BUG B — Content Lab picker escondía clientes del reseller
- Backend ya estaba bien (`c52a1be` deployado en `d04f05a`). **La causa real era frontend**: `useMyClients` ramificaba en `isClient` primero, pero el trigger 00006 auto-crea fila `clients` a TODO usuario → el dueño del reseller tenía `isClient=true` → rama single-client → nunca pedía `/clients/`. → `c12ef86`: prioriza `isOwner` → lista completa.

### Convergencia de calculadores de completitud (3 lugares)
`b312676` alineó ARIA `_sections` al backend `calc_completion_percent` y al frontend `sectionsFilled`. **Wizard = backend = ARIA** ahora cuentan los mismos campos por sección. Verificado por guardian campo por campo (APPROVE).

### Consola — warnings de accesibilidad Radix
`68e14b5`: `DialogTitle/SheetTitle` sr-only + `aria-describedby={undefined}` en `Clients.tsx` (modal wizard desktop+móvil) y `ui/sidebar.tsx` (sheet móvil). Eran la fuente repetida de los ~30 mensajes de consola.

---

## 3 · 🔴 ACCIONES MANUALES DEL OWNER (bloquean ver los fixes en prod)

```bash
# 1. Migraciones (carry-over del 24 may · AÚN pendiente)
cd "D:/Omega Master redes" && supabase db push --linked   # aplica 00020/00021/00022
```
- **Railway (backend)**: auto-deploy OK · confirmá con `curl https://omega-production-3c67.up.railway.app/health` → `git_sha` debe ser `b312676` o posterior. Hoy estaba en `d04f05a` (ARIA X/10 + contexto ya vivos).
- **Vercel (frontend)**: los fixes de **AUDIT 1 (wizard %), AUDIT 2 (picker), a11y consola y BUG A/social** son frontend → **requieren deploy de Vercel + hard-refresh (Ctrl+Shift+R)**. Sin esto, Jorge sigue viendo el bundle viejo (`index-*.js` cacheado).

### Checklist de verificación para Jorge (post-deploy)
1. Hard-refresh.
2. Editar Cliente → el % al editar coincide con el % al guardar (ya no 40 vs 20).
3. Re-guardar las 10 secciones → reabrir → debe verse todo lo elegido (persiste).
4. Content Lab → picker '— Cliente —' lista 'La Milagrosa Software'.
5. Consola → sin warnings de `DialogTitle`.
6. ARIA → "¿qué me falta completar?" → responde "Perfil completado X/10" + secciones ❌.

---

## 4 · Deuda nueva / pendiente

- **DEBT-049** (registrada `fc512b9`): schema fantasma residual fuera del calendar principal — (a) `infrastructure/calendar/calendar_repository.py` (NOVA) usa cols viejas `is_active`/`scheduled_date`; (b) tabla `agent_executions` inexistente referenciada por `system/get_stats`, `omega/*`, `agent_repository`. ~6h · latente (ningún path productivo lo invoca hoy).
- **social_accounts.profile_url**: el wizard captura `profile_url` pero no existe columna → se descarta en el insert (`ec221ed`). Si se quiere preservar, agregar columna o usar `connection_metadata` jsonb (00011). Bajo.
- **§6 `has_existing_content` señal débil**: marcar el checkbox cuenta la sección como llena sin URL · idéntico front+back (no rompe coherencia). Si molesta, cambiar a `existing_followers`/`content_themes` en AMBOS lados a la vez.
- **Contrato único de las 10 secciones** (recomendación guardian): hoy la definición vive duplicada en 3 lugares (`onboarding-completion.ts`, `_onboarding_helpers.py`, `client_context_block._sections`) · convergen pero un cambio de wizard podría desincronizarlos. Considerar centralizar como contrato versionado.
- **Carry-over Sprint 5+**: 4A-2 outcome_evaluator (sin señal real), Capa 2 Haiku (input_sanitizer + GUARDIAN anti-FP), DEBT-040/046/047/048/042/039-V1, `/sentinel/{scan,history,deploy-check}` sin auth.

---

## 5 · Estado de los 3 calculadores de completitud (referencia)

Las 10 secciones (espejo exacto en los 3):
1. Identidad: `name && industry && regions`
2. Negocio: `niche | business_what | business_to_whom | business_diff`
3. Audiencia: `target_audience | audience_age_range | competitors`
4. Voz de marca: `tone | brand_voice_keywords | preferred_formats`
5. Objetivos: `primary_goal | goal_this_month | success_metric`
6. Historial: `has_existing_content | best_post_url | what_worked`
7. Cuentas sociales: `len > 0`
8. Instrucciones: `custom_instructions | emergency_contact_name | preferred_publishing_hours`
9. Identidad visual: `primary_color | logo_file_id`
10. Ejemplos de contenido: `samples len > 0`

---

```
Sesión 25 may · 11 commits · gate 10/10 c/u · guardian APPROVE en cambios de ARIA/AUDIT
Firmado: Claude Opus 4.7 (1M context) + Ibrain Raisen (CEO)
🐢💎 No velocity. Only precision.
```
