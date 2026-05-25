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

## 4 · Continuación post-cierre (25 may · ARIA + Calendario + System)

Bloque de fixes tras §1-3. Todos en origin/main · gate 10/10 c/u · guardian APPROVE. **HEAD: `f807f2c`**.

| Área | Commits | Resumen |
|------|---------|---------|
| **ARIA · deadlock input** | `cece228` | input quedaba mudo: `apiPost`/`apiGet` sin timeout → fetch colgado nunca settla → `isPending` trabado → `disabled` permanente. Wrapper aislado `aria-fetch`: AbortController 35s que cubre fetch **+ body** (`res.json`) → body colgado tras 200 también rechaza. + `onError` toast. (api-client global intacto → Content Lab no afectado) |
| **ARIA · history invertido** | `3a85fe1` | `/aria/history` traía los 50 MÁS VIEJOS (`desc=False`) → mensajes nuevos caían fuera de la ventana al superar 50 → no renderizaban. Fix: `desc=True` + `reversed()` (últimos 50 cronológicos) |
| **ARIA · limit single source** | `493fff7` | `limit=50` duplicado en 3 lugares → ahora solo en el repository (`history.py` y `use_aria_history` forwardean) |
| **Deuda registrada** | `09a77b8` `493fff7` | **DEBT-050** capa multi-agente stubeada (monitor/orchestrator/execute fabrican éxito · P1 cuando dispara · 16h) · **DEBT-051** `aria_repository.py` 99/100L (extraer `fetch_aria_context` · 2h) |
| **Brave timeout** | `ab0a7a4` | 20s→8s · si tarda más, ARIA responde sin contexto web |
| **KPI Posts Programados** | `44ca9d5` | marcaba 0: `.gte(scheduled_for, ahora)` excluía posts cuya hora ya pasó hoy. Fix: ventana desde **inicio del día** + `status IN [pending, scheduled]` |
| **TAREA 2 · 3 botones popup** | `9bd30d7` `0f1bd75` `3b6b1fb` | migración **00025** (`published_manual` en CHECK · DO block) + transición `pending→published_manual` + popup: **Publicar Manual** (→ published_manual) / **Publicar Auto** (disabled · tooltip "requiere cuenta social · MCP") / **Cancelar** |
| **FIX 1 · P1 update_status** | `84a05fe` | devolvía 200 desde el input aunque el UPDATE fallara (safe_insert tragaba) → ahora 500 honesto + respuesta desde la fila persistida |
| **FIX 2 · P5 conteos** | `b2ab2fe` | dashboard/scheduling sumaban solo `published` → ahora `IN [published, published_manual]` (distingue origen, suma en reportes) |
| **FIX 3 + ISSUE 2 · get_stats** | `01ef77c` `aa0c5f8` | `scheduled_posts.is_active` (inexistente → `status='pending'`) + `agents.status` (inexistente → removido) |
| **ISSUE 1 · FK al agendar bloque** | `59d182a` `c9bfdb0` | el localStorage del Content Lab arrastraba content_ids de filas borradas (p.ej. hard-delete cascada) → FK 500. Backend valida existencia+ownership → **409 honesto**; frontend limpia items stale + toast "regeneralos" |
| **get_stats verde** | `f807f2c` | eliminada query `agent_executions` (inexistente · DEBT-049) + `_safe_count` por query (degradación parcial · no try monolítico) + docstrings sincronizados + filtro muerto `clients.neq(deleted)` removido |

**Migración 00025 aplicada** por el owner (`db push`) → `published_manual` habilitado en el CHECK de `scheduled_posts.status`. Backend → Railway · Frontend → Vercel.

**`/system/stats`**: cerrados 2 de 3 dominós (is_active, agents.status) + eliminada query agent_executions → **verde**. DEBT-049 sigue abierta (tabla `agent_executions` real cuando haya telemetría de agentes).

---

```
PENDIENTES_Y_PROGRESOS_20260525.md · sesión 25 may · ~22 commits · gate 10/10 · guardian APPROVE
Firmado: Claude Opus 4.7 (1M context) + Ibrain Raisen (CEO)
🐢💎 No velocity. Only precision.
```
