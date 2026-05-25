# PENDIENTES Y PROGRESOS · 25 may 2026 · CIERRE DE SESIÓN

Sesión de fixes de producción + seguridad + features. Continuación del 24 may.
Owner: Ibrain Raisen (CEO) · Cliente piloto: Jorge / La Milagrosa Software.
~22 commits · gate 10/10 c/u · guardian APPROVE en cambios sensibles · 0 downtime.

---

## 0 · Base del 24 may (ya documentada · ver 20260524.md §10 + SOURCE_OF_TRUTH §11-13)
- **GUARDIAN 4B completo (5 fases)**: migración 00022 (3 tablas+RLS+is_owner) · analyzer heurístico · trigger login + /guardian endpoints · SecurityKPICard (cliente) · SentinelDashboardCard (superadmin).
- **BUG 1+2 ARIA contexto**: doc reaparece al reabrir wizard · ARIA lee el contexto del cliente.
- **Auto-Brave-Search**: ARIA + Content Lab buscan info actual (snippets saneados T2 · cap 3×500).
- **SPRINT 4A**: guardian subagent + builders · input_sanitizer + 5 consumidores · config fail-secure · DEBT-002 analytics honesto.

---

## 1 · Trabajo del 25 may (todos en origin/main)

| Área | Commits | Resumen |
|------|---------|---------|
| **DEBT-031** | `f9fa866` `fc512b9` | calendar legacy eliminado (schema fantasma) + analytics V3 · **DEBT-049 registrada** (NOVA `infrastructure/calendar` + `agent_executions` inexistente · latente ~6h) |
| **AUDIT 1 · wizard %** | `c12ef86` `b312676` | `sectionsFilled` espeja backend (eran falsos positivos de arrays vacíos JS) · 3 calculadores convergen (wizard=backend=ARIA) |
| **AUDIT 2 / BUG B · picker** | `c52a1be` `c12ef86` | `useMyClients` prioriza `isOwner` (trigger auto-crea client a todos → reseller caía en single-client) · backend resuelve resellers desde tabla, no claim |
| **BUG A · wizard persiste** | `7db0fb7` `ec221ed` | zod resiliente en load (data legacy no bloquea) · `username` .max(500) + mapeo a `account_name` (col real) |
| **Wizard 3 fixes** | `546cabd` `98aa557` | deferred upload doc (sube al crear) · campos numéricos texto+parse ("10,000"→10000) · reset blindado (`!isDirty`) · extraído onboarding-error-toast |
| **Regresión create directo** | `f8df3e8` | el hard-delete dejaba sin reseller → 403; fallback a OMEGA Direct (reseller_id es NOT NULL) + SectionSamples deferred-upload |
| **🔒 Seguridad role** | `33166e4` `4c2fb10` `015c6a5` | role/reseller_id derivados server-side de la DB (eran de user_metadata editable → escalada) · fix checks propiedad read/update · índice 00023 (aplicado) · caché TTL-60s |
| **Hard delete cliente** | `4033cd6` `5ff0d27` | DELETE real permanente (cascada FK) vía backend service_role + ownership server-side (antes Supabase directo → RLS bloqueaba → toast falso) |
| **Logo overlay (Fase 1)** | `5358f7f` | toggle "Usar mi logo" opt-in → Pillow overlay (esq inf-der · 10%·20px·80%) · best-effort · default sin logo |
| **ARIA contexto** | `d115222` `c8973af` `331b989` | contexto ampliado + "Perfil X/10" ✅/❌ + regiones (clients.region) · cap 2000 |
| **a11y + deploy** | `68e14b5` `d04f05a` | DialogTitle sr-only (limpia consola Radix) · git_sha en /health |

---

## 2 · 🔴 ACCIONES DEL OWNER / ESTADO DE DEPLOY

1. **Migraciones: TODAS aplicadas** (hasta `00023` · `supabase db push --linked` corrido esta sesión · índice `resellers.owner_user_id` activo). **NO hay migración pendiente.**
2. **Railway DEBE REBUILDEAR** por la dependencia nueva **Pillow** (es build de nixpacks, **NO** un `db push`). Verificá `/health` → `git_sha` ≥ `5358f7f`. ⚠️ nixpacks tuvo fricciones antes — vigilá el log del build; si falla, reportarlo.
3. **Vercel** debe deployar el frontend (AUDIT 1/2 wizard %, picker, wizard 3 fixes, toggle logo, a11y consola) + **hard-refresh (Ctrl+Shift+R)**. Si el bundle viejo persiste, "Clear build cache" en Vercel.

### Verificación end-to-end para Jorge (post-deploys)
1. Nuevo Cliente → llenar 9-10 secciones → Crear → reabrir → **todo persiste** (incl. doc subido y campos numéricos con comas).
2. Wizard: el % al editar **coincide** con el guardado (no más 40 vs 20).
3. Content Lab: picker lista **La Milagrosa Software**.
4. Eliminar cliente → desaparece y **no vuelve** tras hard-refresh (Supabase: 0 records).
5. Generar imagen con toggle "Usar mi logo" + cliente con logo → logo abajo-derecha; sin toggle → sin logo.
6. ARIA: "¿qué me falta completar?" → "Perfil X/10" + secciones ❌ + regiones.

---

## 3 · Deuda / pendientes

- **DEBT-049** (nueva): NOVA `infrastructure/calendar` (cols viejas) + `agent_executions` inexistente (system/omega) · latente · ~6h.
- **Seguridad transversal**: otros endpoints aún autorizan con `user["role"]` del claim (admin/*, reseller/*, social_accounts/*). El claim ya no es forjable post-`33166e4` (role derivado de DB), pero conviene migrar esos gates a verificación server-side por datos (patrón clients/delete). Blast radius reportado.
- **Logo Fase 2**: persistir el logo subido en Content Lab → `brand_files` (categoría 'logo') + `client_brand_assets.logo_file_id` (hoy el wizard captura `logo_files` como File pero no los persiste).
- **Video con logo**: requiere ffmpeg (fuera de scope · video sale sin logo = actual).
- **Caché de rol**: per-process · revocación de privilegio tarda ≤60s (documentado · si se necesita inmediata, exponer `_role_cache.pop(user_id)`).
- **Carry-over previos**: 4A-2 outcome_evaluator · Capa 2 Haiku · DEBT-040/046/047/048/042/039-V1 · `/sentinel/{scan,history,deploy-check}` sin auth.

---

```
PENDIENTES_Y_PROGRESOS_20260525.md · sesión 25 may · ~22 commits · gate 10/10 · guardian APPROVE
Firmado: Claude Opus 4.7 (1M context) + Ibrain Raisen (CEO)
🐢💎 No velocity. Only precision.
```
