# PENDIENTES Y PROGRESOS · 26 may 2026

> Handoff de cierre de sesión · OmegaRaisen · 🐢💎 No velocity, only precision.
> Estado granular vivo: `ESTADO_OMEGA.md` · Deuda detallada: `SOURCE_OF_TRUTH.md §6`.
> **La próxima sesión arranca con DEBT-049.**

---

## 0 · ARRANQUE PRÓXIMA SESIÓN → DEBT-049 (🟠 8h)

`agent_executions` inexistente + alinear `agent_repository.py` (subsume DEBT-077 caso B).
- **(a)** Crear migración `agent_executions` (agent_id/status/started_at/execution_time_ms/client_id/...) — el repo y `system/get_stats` / `omega/get_activity` / `omega/get_dashboard` la referencian; cualquier llamada da 500.
- **(b)** Alinear `agent_repository.py`: `find_by_agent_id` usa `agent_id` (real `code`) → 404 en `/agents/{id}/execute` (VIVO); `create_execution`/`update_execution` → tabla inexistente → 500; `create_log`/`find_logs` (a `agent_log`) son métodos muertos.
- **(c)** `infrastructure/calendar/calendar_repository.py` (NOVA `_agent_routing`) usa cols viejas `is_active`/`scheduled_date` (real V3: `scheduled_for`/`status`).
- **Desbloquea:** DEBT-052 (créditos por agente · revenue) + DEBT-053 (Posts Tab ROI por agente).
- Patrón: investigar → declarar plan por sub-caso → Fork Mode → gate + guardian c/u.

---

## 1 · LO QUE SE HIZO HOY (todo pusheado a `origin/main`)

### Quick wins (Fork Mode)
- Content cards tipo imagen → `<img>` thumbnail + fallback (`4305857`)
- Media: acciones hover por card (copiar URL · usar en Content Lab · descargar) (`34ad276`)
- **DEBT-064 cerrada** · desmonta router legacy `/content-lab` (`d23c632` · `ef59397`)

### Rediseño Dashboard (6 cambios + migración 00028)
- C2 tooltip donut blanco (`9a651bc`) · C5 Actividad Reciente 3 items + modal con filtro (`89e7093`)
- **Migración 00028** `aria_suggestions` (`a8e341f` · **aplicada**)
- C1 backend `POST/GET/PATCH /aria/suggestions` rule-based (`e3e14b6`) · C3 gráfica Actividad de Agentes (`55bf120`) · C4 card Observaciones (`eef0e42`) · C1 frontend + cableado (`fc6e068`)
- Tweaks: "Ver historial" verde header outline (`1c3ef42`/`6a8605b`) · foto ARIA banner en Sugerencias (`dc666bf`)

### Auditoría Dashboard P1 + 3 fixes
- Auditoría read-only (detectó: botón scan que mentía · filtro `'scheduled'` muerto · próximo post solo mes actual)
- Fixes (`32a2f61`): botón Seguridad → `refetch()` real + toast honesto · `'scheduled'` removido del filtro · `useNextScheduledPost` (próximo post cross-mes)

### Docs comerciales · 3 planes definitivos
- `MODELO_NEGOCIO v1.1` + `SOURCE_OF_TRUTH §15` (`17d1e74`): Básico $29/89% · PRO $65/88% · Enterprise $199/83% · Video Packs (69/74/81%) · proyección a escala (mix 60/30/10 · ARPU ~$57)

### Sección Planes en Add-Ons (exec diferido · P1)
- 3 cards + downgrade dialog con checkbox obligatorio · "Confirmar" disabled + tooltip (`2447b16`). `plan-limits.ts` Enterprise corregido ($199/192/3).
- **DEBT-076 registrada** (backend cambios de plan · downgrade fin-de-ciclo + checkout Enterprise · 🟡 6h · Sprint 5) (`31f077d`)

### 3 cambios página cliente
- Lista `/clients`: ⋮ → 3 inline (Ver verde · editar · eliminar con confirm AlertDialog) (`582d872`)
- `/clients/:id`: quita barra de plan duplicada (`ce8bc9e`) · Tab AI copy comercial (Anthropic protagonista · sin "excepción de infraestructura") (`88289f3`)

### SENTINEL fix (score destrabado)
- **TAREA 2** reglas al stack actual: `TAVILY_API_KEY`→`BRAVE_API_KEY` · tablas reales (`omega_agent_memory`→`agent_memory`, removidas 5 fantasma) — **el DB Guardian estaba clavado en 0/100 por 6 tablas fantasma × -25 CRITICAL** (`1d4d7da`)
- **Migración 00029** `sentinel_persistence` (3 tablas internas · **aplicada**) (`8114df6`) + persistencia best-effort (`111d032`)
- **TAREA 3** comentario `aria_4` routing (`ef87e9b`)

### Auditoría schema + DEBTs 077/078/079
- Audit read-only: gap migración (falta `00009`) · ~15 tablas fantasma en código · vista `agent_performance_stats` expuesta
- **DEBT-079 cerrada** · elimina logging muerto a `omega_tool_calls` (`91b14d2`)
- **DEBT-078 cerrada** · **migración 00030** revoke `agent_performance_stats` (**aplicada**) (`1635884`)
- web_search description "via Tavily"→"via Brave" (`1db9e5f`)
- Tab Agente: agentes activos del cliente + CTA "Explorar Agentes →" (vacío honesto hoy) (`702379a`)

### DEBT-077 resuelta (schema drift estructural · 3 casos)
- **Caso A** · **migración 00031** `agent_working_memory` (tabla nueva · separa memoria de trabajo del training corpus) + rename en 8 archivos (`25ab75a` · **aplicada**)
- **Caso B** · subsumido en DEBT-049 (agent_repository alignment)
- **Caso C** · elimina dead code flujo solicitudes/upsell (borra paquetes admin/ + upsell/) (`91adfff`)
- Cierre docs (`7d23db2`)

---

## 2 · MIGRACIONES — todas aplicadas (db push por owner)
`00028` aria_suggestions · `00029` sentinel_persistence · `00030` revoke_agent_stats · `00031` agent_working_memory. **Cero migraciones pendientes.** (Nota: la secuencia salta `00009` — gap histórico · no funcional.)

## 3 · DEBTs cerradas hoy
DEBT-064 (router legacy) · DEBT-077 (schema drift A/B/C) · DEBT-078 (vista revocada) · DEBT-079 (tool_calls muerto).
Registradas hoy: DEBT-076 · DEBT-077 (→resuelta) · DEBT-078 (→resuelta) · DEBT-079 (→resuelta).
**Deuda total: ~710.5h** (ver `SOURCE_OF_TRUTH §6` / `ESTADO §3`).

## 4 · ESTADO DEL SISTEMA
- **Backend** (Railway) + **Frontend** (Vercel) desplegados con todo lo de hoy.
- **SENTINEL**: DB Guardian salió de 0/100 (tablas reales) + persistencia funciona (00029) → score esperado **≥85** (validar corriendo un scan superadmin + `/sentinel/status`).
- **agent_working_memory** (00031) aplicada → NOVA/handoff/oracle ahora persisten de verdad (dejaron de fallar-soft).
- **agent_performance_stats** revocada a authenticated/anon (00030) → cerrado el "Unrestricted" de Supabase.
- Demo Mode (`cliente@omega.com`) activo · planes con toggle Vista.

## 5 · DEUDA ABIERTA PRINCIPAL (orden sugerido)
1. **DEBT-049** (🟠 8h) — agent_executions + agent_repository alignment · **arranque próxima sesión** · desbloquea DEBT-052/053.
2. **DEBT-050** (🟠 16h) — capa multi-agente stubeada (monitor siempre-verde · execute_agent fallback fabrica éxito · **P1 cuando dispara**).
3. **DEBT-040** (🔴 80h) — OAuth Meta + Google (publicación real · Sprint 5-6).
4. **DEBT-074** (🟠 4h) — `safe_insert` sync bloquea event loop (transversal).
5. **DEBT-076** (🟡 6h) — backend cambios de plan (downgrade fin-de-ciclo + checkout Enterprise) · Sprint 5.
6. **DEBT-060** (🟠 2h) — bucket `media` inexistente en migraciones.

## 6 · LEFTOVERS HONESTOS (🟢 · no bloquean)
- 6 comentarios/docstrings aún dicen "omega_agent_memory" (el `.table()` ya apunta a `agent_working_memory` · cosmético).
- `get_briefing.py` order by `priority` con casing mixto (URGENT/HIGH vs high) → orden no semántico · pre-existente.
- `legacy/` untracked en git (respaldos · considerar `.gitignore`).
- Sección Planes / Tab Agente / downgrade dialog: UI completa pero **exec diferido** (sin backend de compra de agentes ni cambio de plan · honesto · CTA/disabled).

---

> **Disciplina mantenida toda la sesión:** declarar antes de tocar · Fork Mode (subagentes escriben+validan · guardian audita · main commitea) · gate `validate-before-push.sh` 10/10 c/u · 1 commit por módulo · staging explícito · push solo bajo pedido. 🐢💎
