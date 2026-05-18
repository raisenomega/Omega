# OmegaRaisen

> Plataforma SaaS multi-tenant white-label para automatización de redes sociales con agentes IA organizados bajo NOVA (CEO Agent) y supervisados por SENTINEL.

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Stack](https://img.shields.io/badge/stack-Vite%20%2B%20FastAPI%20%2B%20Supabase-blue.svg)](#stack)
[![AI](https://img.shields.io/badge/AI-Anthropic%20Claude%204.7-orange.svg)](#ai-providers)

---

## Qué es

OmegaRaisen sustituye un equipo humano de marketing digital (community manager, copywriter, diseñador, estratega, analista) por 37+ agentes IA orquestados. Una agencia opera 50+ cuentas de cliente con 1-2 humanos supervisores en lugar de 10-15.

**Capacidades:**
- Generación de contenido multi-formato (texto, imagen, video) alineado a brand voice por cliente
- Calendario editorial inteligente con timing óptimo
- Distribución multi-plataforma (Instagram, Facebook, Twitter, LinkedIn, TikTok, YouTube)
- Analytics consolidados con sentiment analysis
- Inteligencia competitiva en tiempo real
- Gestión de crisis con drafts (humano aprueba publicación)
- Multi-tenant white-label (cada reseller con branding propio)
- NOVA: CEO Agent conversacional para owner/reseller/cliente

---

## Stack

```
Frontend       Vite 5 + React 18 + TypeScript 5.8 + shadcn/ui + Tailwind
Backend        Python 3.11 + FastAPI 0.109 + Pydantic 2 + SQLAlchemy 2
Database       Supabase (PostgreSQL 15 + pgvector + RLS)
Deploy         Vercel (frontend) + Railway (backend) + Supabase Cloud (DB)
```

## AI Providers

```
TEXTO/RAZONAMIENTO    Anthropic Claude — ÚNICO proveedor
                      claude-haiku-4-5-20251001  (clasificación, hashtag-gen)
                      claude-sonnet-4-6          (default — content, strategy)
                      claude-opus-4-7            (decisiones críticas)

IMÁGENES              Google Nano Banana — excepción documentada (DDD I1)
                      gemini-3.1-flash-image-preview  (default)
                      gemini-3-pro-image-preview      (premium — texto en imagen)

VIDEO                 Google Veo 3.1 — excepción documentada (DDD I1)
                      veo-3.1-generate-preview       (default, 8s · 1080p · audio nativo)
                      veo-3.1-lite-generate-preview  (alto volumen, mismo speed)
```

Ver `DDD_REGLAS_OMEGA.md` Categoría I para justificación de excepciones.

---

## Quick start (desarrollo local)

### Prerequisitos
- Node.js ≥ 20 LTS
- Python 3.11
- Supabase CLI (`npm i -g supabase`)
- Cuenta Anthropic + Google AI Studio + Supabase

### Setup

```bash
# 1. Clone
git clone https://github.com/raisenomega/Omega.git
cd Omega

# 2. Identidad git (CRÍTICO — ver PROTOCOLO_IDENTIDAD_GIT_OMEGA.md)
bash scripts/setup-git-identity.sh

# 3. Frontend deps
npm install

# 4. Backend deps
cd backend && python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# 5. Environment
cp .env.example .env
# Editar .env con tus keys (NUNCA commitear)

# 6. Database
supabase link --project-ref rwlnihoqhxwpbehibgxu
supabase db push

# 7. Validate before first commit
bash scripts/validate-before-push.sh   # debe pasar 9/9

# 8. Run
# Terminal 1: frontend
npm run dev
# Terminal 2: backend
cd backend && uvicorn app.main:app --reload
```

Open http://localhost:5173

---

## Estructura del repo

```
Omega/
├── src/                                  Frontend Vite + React
│   ├── bc-01-clients/                    Bounded Context: clientes
│   ├── bc-02-content-lab/                Bounded Context: generación
│   ├── bc-03-calendar/                   Bounded Context: scheduling
│   ├── bc-04-analytics/                  Bounded Context: métricas
│   ├── bc-05-resellers/                  Bounded Context: white-label
│   ├── bc-06-sentinel/                   Bounded Context: security
│   ├── bc-07-oracle/                     Bounded Context: intelligence brief
│   ├── bc-cognition/                     Bounded Context: AI orchestration
│   └── components/ui/                    shadcn/ui (autogenerado)
│
├── backend/
│   ├── app/
│   │   ├── api/routes/                   38 routers FastAPI
│   │   ├── agents/                       22 agentes IA (refactor en Phase 3)
│   │   ├── bc_cognition/                 ✨ NUEVO V3
│   │   │   ├── domain/
│   │   │   │   ├── persona_nova.py       System prompt CEO
│   │   │   │   ├── limits_omega.py       Guardrails (SHA1 verificado)
│   │   │   │   ├── conviction.py         Regla P3 (confidence ≥ 7)
│   │   │   │   └── routing_table.py      Haiku/Sonnet/Opus
│   │   │   ├── application/
│   │   │   └── infrastructure/
│   │   │       ├── anthropic_adapter.py  ÚNICO entry point Claude
│   │   │       ├── nano_banana_adapter.py
│   │   │       └── veo3_adapter.py
│   │   ├── services/                     Servicios transversales
│   │   ├── workers/                      Cron jobs APScheduler (8 jobs)
│   │   ├── domain/                       Tipos de dominio
│   │   ├── infrastructure/               Adapters (Supabase, etc.)
│   │   └── main.py                       FastAPI app entry
│   ├── requirements.txt
│   └── nixpacks.toml                     Railway config
│
├── supabase/
│   └── migrations/                       Migraciones SQL consolidadas
│
├── .claude/                              Claude Code stack
│   ├── settings.json
│   ├── hooks/                            Enforcement determinístico
│   ├── agents/                           Subagentes especializados
│   └── skills/                           Procedimientos reutilizables
│
├── scripts/                              CI/CD + verificaciones
│   ├── validate-before-push.sh           Pre-push hook (9 checks)
│   ├── verify-guardrails.sh              SHA1 baseline check
│   └── bootstrap.sh                      Setup inicial
│
└── docs/                                 Documentación
    ├── SOURCE_OF_TRUTH.md                ⭐ leer al inicio de cada sesión
    ├── PRD_RECONSTRUIDO.md
    ├── CLAUDE.md                         ≤60L · constitución del proyecto
    ├── DDD_REGLAS_OMEGA.md               Contrato técnico
    ├── PROTOCOLO_SEGURIDAD_OMEGA.md      Seguridad CIA-level
    ├── PROTOCOLO_IDENTIDAD_GIT_OMEGA.md  Identidad por repo
    ├── PLANTILLA_OMEGA_V3.md             Plantilla universal adaptada
    └── MIGRATION_PLAN_OMEGA.md           Plan de fases
```

---

## Reglas inviolables

Resumen — ver `DDD_REGLAS_OMEGA.md` para detalle.

```
P1 — Verdad brutal. Cero datos sintéticos en dashboards de cliente.
P2 — La marca del cliente es el activo. Cero acción que la dañe sin firma humana.
P3 — Confidence < 7 OR brand_voice_check fail → hold_for_human_review.
P4 — Crisis manager NUNCA responde solo. Solo alerta + draft.
P5 — Cada decisión registrada con was_correct eventual.

A2  — Domain puro (cero imports externos)
I1  — Solo Anthropic (Nano Banana + Veo 3.1 son excepciones documentadas)
G1  — Guardrails con SHA1 verificado
M1  — agent_memory + pgvector desde día 1
T4  — Pre-push hook 9/9 verde sin excepción
```

---

## Comandos esenciales

```bash
# Desarrollo
npm run dev                    Frontend con HMR
cd backend && uvicorn app.main:app --reload   Backend con auto-reload

# Build
npm run build                  Frontend dist/
# Backend: auto-deploy en Railway al push

# Testing
npm test                       Vitest (frontend)
cd backend && pytest           Pytest (backend)
npx promptfoo eval             Evals bc_cognition

# Validación pre-push
bash scripts/validate-before-push.sh

# Database
supabase migration new <name>
supabase db push
supabase db reset              # local solo

# Deploy
git push origin main           Vercel + Railway auto-deploy
```

---

## Deploy

### Frontend (Vercel)
- Auto-deploy on push to `main`
- Preview deploys on PRs
- Custom domain: `r-omega.agency`

### Backend (Railway)
- Auto-deploy on push to `main`
- Nixpacks build (Python 3.11)
- Health: `/health` · Docs: `/docs`

### Database (Supabase)
- Migrations via Supabase CLI o `supabase db push`
- Backups diarios automáticos
- Pooler URL para SQLAlchemy

Ver `MIGRATION_PLAN_OMEGA.md` para setup inicial.

---

## Documentación

| Documento | Para qué |
|-----------|----------|
| `INDICE_PROYECTO.md` | 🗺️ Mapa maestro · orden de lectura · gates de readiness. **LEER PRIMERO**. |
| `IDENTIDAD_GIT_CRITICA.md` | ⚠️ Leer ANTES de cualquier git operation. |
| `SOURCE_OF_TRUTH.md` | Leer ANTES de cada sesión. Qué existe, qué no, deudas. |
| `PRD_RECONSTRUIDO.md` | Visión del producto reconstruida desde el código. |
| `CLAUDE.md` | Constitución para sesiones de Claude Code. |
| `DDD_REGLAS_OMEGA.md` | Contrato técnico inviolable. |
| `BC_COGNITION_OMEGA.md` | Arquitectura del cerebro IA (37 agentes). |
| `MCP_ARSENAL_OMEGA.md` | Catálogo de MCPs/APIs · roadmap de activación. |
| `PROTOCOLO_SEGURIDAD_OMEGA.md` | Defensa en profundidad CIA-level. |
| `PROTOCOLO_IDENTIDAD_GIT_OMEGA.md` | Setup includeIf por proyecto. |
| `PLANTILLA_OMEGA_V3.md` | Plantilla universal V3 adaptada a OmegaRaisen. |
| `MIGRATION_PLAN_OMEGA.md` | Plan operacional de migración por fases. |

---

## Contributing

Este repositorio es **propiedad de Raisen Agency** y NO acepta contribuciones externas.

Para contribuyentes internos:
1. Lee `CLAUDE.md` ANTES de la primera línea de código
2. Verifica identidad git con `git config user.email` (debe ser `raisenagencypr@gmail.com`)
3. Antes de cada push: `bash scripts/validate-before-push.sh` debe pasar 9/9
4. Cambios ≥3 archivos: usa Plan Mode de Claude Code
5. Cambios en `bc_cognition/domain/limits_omega.py`: requieren test que falla primero + rotación SHA1

---

## Soporte

- **Owner:** Ibrain Raisen — Raisen Agency
- **Email:** raisenagencypr@gmail.com
- **Status:** SENTINEL en `/api/v1/sentinel/scan/full`

---

## License

Proprietary © 2026 Raisen Agency. All rights reserved.

🐢💎 No velocity, only precision.
