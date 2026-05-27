"""
OmegaRaisen FastAPI Application
Main entry point for the backend API
37 AI Agents | 101 Endpoints | Enterprise Social Media Automation
"""
# DEBT-028: cargar .env a os.environ para legacy os.getenv() reads
# (33 sites en 21 archivos pendientes de migración a settings.xxx · DEBT-029)
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.rate_limit_middleware import RateLimitMiddleware
from app.config import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy import create_engine
from app.services.sentinel_service import SentinelService
from app.services.oracle_service import OracleService
from app.workers.news_monitor_worker import NewsMonitorWorker
from app.workers.competitor_tracker_worker import CompetitorTrackerWorker
from app.workers.trend_spotter_worker import TrendSpotterWorker
import logging
import os

logger = logging.getLogger(__name__)

# Optional Qdrant import
try:
    from app.infrastructure.vector_store.qdrant_client import initialize_qdrant
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant dependencies not installed yet")

from app.api.routes import (
    content, strategy, analytics, engagement, monitor, brand_voice, competitive, trends, crisis,
    reports, growth, video_production, scheduling, ab_testing, orchestrator, resellers, auth,
    context, clients, social_accounts, brand_files, agents,
    system, omega, nova, sentinel, oracle, prompt_vault, handoff, reseller, sub_brands
)
# DEBT-036: módulo billing legacy desregistrado · reemplazado por billing_v3 bc_billing
from app.api.routes import billing_v3
from app.api.routes.oauth.router import router as oauth_router
from app.api.routes import publishing
from app.api.routes import aria_v1
from app.api.routes import clients_v3
from app.api.routes import content_v3
from app.api.routes import calendar_v3
from app.api.routes import content_lab_v3
from app.api.routes import intelligence
from app.api.routes import brand_voice_v2
from app.api.routes import guardian
from app.sentinel.persistence_router import router as sentinel_persistence_router
from app.api.routes.clients.feature_usage_router import router as feature_usage_router

# Services & scheduler
sentinel_service = SentinelService()
oracle_service = OracleService()
scheduler = AsyncIOScheduler(timezone="America/Puerto_Rico")


def _persistent_jobstore_or_none() -> "SQLAlchemyJobStore | None":
    """DEBT-047 · jobstore persistente (los jobs sobreviven restarts) DEPLOY-SAFE.
    Railway corre Python 3.11 (nixpacks · python311) → SQLAlchemy 2.0.25 instancia OK
    (el 'incompat con 3.13' de DEBT-045 no aplica al runtime desplegado · verificado).
    Verifica conectividad ANTES de comprometer el jobstore · ante CUALQUIER fallo
    (URL no parseable, DB caída, sin permiso) → None → el scheduler cae al MemoryJobStore
    default · NUNCA rompe el arranque."""
    raw = (settings.database_url or "").strip()
    if not raw:
        return None
    url = raw.replace("postgres://", "postgresql+psycopg2://", 1) if raw.startswith("postgres://") else raw
    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect():
            pass
        return SQLAlchemyJobStore(engine=engine)
    except Exception as e:
        logger.warning(f"DEBT-047 · jobstore persistente no disponible → in-memory: {e}")
        return None

# Create FastAPI application
app = FastAPI(
    title="OmegaRaisen API", version="2.0.0",
    description="Social Media Automation — 37 AI Agents | Enterprise Platform",
    docs_url="/docs", redoc_url="/redoc",
)

# DEBT-070: rate limiting por IP · cablea settings.rate_limit_per_minute (antes config
# muerta). Se monta ANTES de CORS → CORS queda outermost (Starlette: último add = outer) →
# el 429 pasa por CORS y lleva los headers al browser.
app.add_middleware(RateLimitMiddleware, limit_per_minute=settings.rate_limit_per_minute)

# Configure CORS · lee BACKEND_CORS_ORIGINS (CSV) via settings.cors_origins_list.
# Fallback ["*"] solo si la env var está vacía (dev local). El browser rechaza
# allow_credentials=True con wildcard "*" · por eso se desactiva en ese caso.
_cors_origins = settings.cors_origins_list or ["*"]
_allow_creds = _cors_origins != ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    if QDRANT_AVAILABLE:
        await initialize_qdrant()
    else:
        logging.warning("Skipping Qdrant initialization")
    # DEBT-047 · jobstore persistente deploy-safe (cae a in-memory si la DB no responde)
    _jobstore = _persistent_jobstore_or_none()
    if _jobstore is not None:
        scheduler.add_jobstore(_jobstore, "default")
        logger.info("DEBT-047 · jobstore persistente (SQLAlchemy) activo")
    else:
        logger.info("DEBT-047 · jobstore in-memory (fallback)")
    # SENTINEL cron jobs · replace_existing=True → idempotente con jobstore persistente
    scheduler.add_job(sentinel_service.run_vault_scan, 'cron', hour=2, minute=0, id='vault_scan', replace_existing=True)
    scheduler.add_job(sentinel_service.run_db_guardian, 'cron', hour=5, minute=0, id='db_guardian', replace_existing=True)
    scheduler.add_job(sentinel_service.run_full_scan, 'cron', hour=7, minute=0, id='sentinel_brief', replace_existing=True)
    scheduler.add_job(sentinel_service.run_pulse_monitor, 'interval', minutes=5, id='pulse_monitor', replace_existing=True)
    # ORACLE cron jobs
    scheduler.add_job(oracle_service.generate_intelligence_brief, 'cron', day_of_week='mon', hour=7, minute=0, id='oracle_weekly_brief', replace_existing=True)
    # OMEGA Workers v2
    news_worker = NewsMonitorWorker()
    scheduler.add_job(news_worker.run_all_clients, 'interval', hours=2, id='news_monitor', max_instances=1, replace_existing=True)
    competitor_worker = CompetitorTrackerWorker()
    scheduler.add_job(competitor_worker.run_all_clients, 'interval', hours=6, id='competitor_tracker', max_instances=1, replace_existing=True)
    trend_worker = TrendSpotterWorker()
    scheduler.add_job(trend_worker.run_all_clients, 'interval', hours=12, id='trend_spotter', max_instances=1, replace_existing=True)
    # BRAND DNA refresh (DEBT-044 Sprint 2 · 9no cron job)
    from app.bc_cognition.application.use_brand_dna import refresh_all_brand_dna
    scheduler.add_job(refresh_all_brand_dna, 'cron', hour=3, minute=0, id='brand_dna_refresh', replace_existing=True)
    # VIDEO ORPHAN cleanup (DEBT-045 Sprint 3 · 10mo cron job)
    from app.bc_cognition.application.cleanup_orphan_video_jobs import cleanup_orphan_video_jobs
    scheduler.add_job(cleanup_orphan_video_jobs, 'interval', hours=1, id='video_jobs_orphan_cleanup', max_instances=1, replace_existing=True)
    # OUTCOME EVALUATOR (4A-2 · PASO 3 ciclo auto-aprendizaje · 11vo cron job)
    from app.bc_cognition.application.outcome_evaluator import run_outcome_evaluation
    scheduler.add_job(run_outcome_evaluation, 'cron', hour=4, minute=0, id='outcome_evaluator', replace_existing=True)
    # CREDIT PERIOD RESET (DEBT-052 FASE 4 · fin-de-mes · 12vo cron job)
    from app.bc_billing.application.reset_credit_periods import run_credit_period_reset
    scheduler.add_job(run_credit_period_reset, 'cron', hour=0, minute=5, id='credit_period_reset', max_instances=1, replace_existing=True)
    # DECISION EVALUATOR (DEBT-100 · ARIA_LEARNING_LOOP Loop 1 · cierra was_correct · cada hora :30 · 13vo cron job)
    from app.workers.decision_evaluator_worker import run_decision_evaluator_job
    scheduler.add_job(run_decision_evaluator_job, 'cron', minute=30, id='decision_evaluator', max_instances=1, replace_existing=True, misfire_grace_time=300)
    scheduler.start()
    logger.info("✅ SENTINEL + ORACLE + OMEGA + BRAND_DNA + ORPHAN_CLEANUP + OUTCOME_EVAL + CREDIT_RESET + DECISION_EVAL workers activos — 13 jobs (jobstore persistente DEBT-047)")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    scheduler.shutdown()
    logger.info("SENTINEL schedulers detenidos")

# Core Agents (1-5)
app.include_router(content.router, prefix=settings.api_v1_prefix, tags=["Content Creator"])
app.include_router(strategy.router, prefix=settings.api_v1_prefix, tags=["Strategy"])
app.include_router(analytics.router, prefix=settings.api_v1_prefix, tags=["Analytics"])
app.include_router(engagement.router, prefix=settings.api_v1_prefix, tags=["Engagement"])
app.include_router(monitor.router, prefix=settings.api_v1_prefix, tags=["Monitor"])

# Intelligence Agents (6-9)
app.include_router(brand_voice.router, prefix=settings.api_v1_prefix, tags=["Brand Voice"])
app.include_router(competitive.router, prefix=settings.api_v1_prefix, tags=["Competitive Intel"])
app.include_router(trends.router, prefix=settings.api_v1_prefix, tags=["Trend Hunter"])
app.include_router(crisis.router, prefix=settings.api_v1_prefix, tags=["Crisis Manager"])

# Production Agents (10-14)
app.include_router(reports.router, prefix=settings.api_v1_prefix, tags=["Report Generator"])
app.include_router(growth.router, prefix=settings.api_v1_prefix, tags=["Growth Hacker"])
app.include_router(video_production.router, prefix=settings.api_v1_prefix, tags=["Video Production"])
app.include_router(scheduling.router, prefix=settings.api_v1_prefix, tags=["Scheduling"])
app.include_router(ab_testing.router, prefix=settings.api_v1_prefix, tags=["A/B Testing"])

# Master Orchestrator (15)
app.include_router(orchestrator.router, prefix=settings.api_v1_prefix, tags=["Orchestrator ⭐"])

# Multi-Tenant Infrastructure
app.include_router(resellers.router, prefix=settings.api_v1_prefix, tags=["Resellers 🏢"])
app.include_router(auth.router, prefix=settings.api_v1_prefix, tags=["Auth 🔐"])
app.include_router(billing_v3.router, prefix=settings.api_v1_prefix, tags=["Billing 💳"])
app.include_router(oauth_router, prefix=settings.api_v1_prefix)
app.include_router(publishing.router, prefix=settings.api_v1_prefix, tags=["Publishing"])
app.include_router(aria_v1.router, prefix=settings.api_v1_prefix, tags=["ARIA"])
app.include_router(clients_v3.router, prefix=settings.api_v1_prefix, tags=["Clients V3"])
app.include_router(content_v3.router, prefix=settings.api_v1_prefix, tags=["Content V3"])
app.include_router(calendar_v3.router, prefix=settings.api_v1_prefix, tags=["Calendar V3"])
app.include_router(content_lab_v3.router, prefix=settings.api_v1_prefix, tags=["Content Lab V3"])
app.include_router(intelligence.router, prefix=settings.api_v1_prefix, tags=["Intelligence 🧠"])
app.include_router(brand_voice_v2.router, prefix=settings.api_v1_prefix, tags=["Brand Voice V2"])
app.include_router(context.router, prefix=settings.api_v1_prefix)
app.include_router(clients.router, prefix=settings.api_v1_prefix, tags=["Clients 👥"])
app.include_router(social_accounts.router, prefix=settings.api_v1_prefix, tags=["Social Accounts 📱"])
app.include_router(brand_files.router, prefix=settings.api_v1_prefix, tags=["Brand Files 📎"])
# DEBT-064: legacy content_lab.router DESMONTADO · 100% superseded por content_lab_v3 (:160).
# Colisionaba en prefix /content-lab. Ninguna ruta legacy-only es usada por el frontend.
# El paquete content_lab NO se borra: builders.prompt_builder lo usa content_lab_prompt_service.
# DEBT-031: legacy calendar.router eliminado · 100% superseded por calendar_v3 (schema V3 real)
app.include_router(agents.router, prefix=settings.api_v1_prefix, tags=["Agents 🤖"])
app.include_router(system.router, prefix=settings.api_v1_prefix, tags=["System 🔧"])
app.include_router(omega.router, prefix=settings.api_v1_prefix, tags=["OMEGA Company 👑"])
app.include_router(nova.router, prefix=settings.api_v1_prefix, tags=["NOVA 👑"])
app.include_router(sentinel.router, prefix=settings.api_v1_prefix, tags=["SENTINEL 🛡️"])
app.include_router(sentinel_persistence_router)
app.include_router(guardian.router, prefix=settings.api_v1_prefix, tags=["GUARDIAN 🛡️"])
app.include_router(oracle.router, prefix=settings.api_v1_prefix + "/oracle", tags=["ORACLE 🔮"])
app.include_router(prompt_vault.router, prefix=settings.api_v1_prefix, tags=["Prompt Vault 📚"])
app.include_router(handoff.router, prefix=settings.api_v1_prefix, tags=["Handoff Protocol 🤝"])
app.include_router(reseller.router, prefix=settings.api_v1_prefix, tags=["Reseller Dashboard 🏢"])
app.include_router(feature_usage_router, prefix=settings.api_v1_prefix, tags=["Feature Usage 📊"])
app.include_router(sub_brands.router, prefix=settings.api_v1_prefix, tags=["Sub-Brands 🏷️"])

@app.get("/")
async def root() -> dict[str, str | int]:
    """Root endpoint with dynamic stats"""
    from app.api.routes.system.handlers.get_stats import count_routes, get_supabase_service
    total_endpoints = count_routes(app)
    try:
        supabase = get_supabase_service()
        agents_resp = supabase.client.table("agents").select("id", count="exact").eq("is_active", True).execute()
        total_agents = agents_resp.count if agents_resp.count else 37
    except:
        total_agents = 37
    return {
        "message": "OmegaRaisen API", "version": "2.0.0", "status": "running",
        "agents": f"{total_agents}/{total_agents}", "endpoints": str(total_endpoints), "docs": "/docs"
    }

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    from app.api.routes.system.handlers.get_stats import get_supabase_service
    try:
        supabase = get_supabase_service()
        agents_resp = supabase.client.table("agents").select("id", count="exact").eq("is_active", True).execute()
        total_agents = agents_resp.count if agents_resp.count else 37
    except:
        total_agents = 37
    return {"status": "healthy", "version": "2.0.0", "agents": f"{total_agents}/{total_agents}", "environment": settings.environment, "git_sha": os.getenv("RAILWAY_GIT_COMMIT_SHA", "unknown")[:7]}

@app.get(f"{settings.api_v1_prefix}/status")
async def api_status() -> dict[str, str | bool]:
    """API status endpoint"""
    return {"api_version": "v1", "status": "operational", "debug_mode": settings.debug, "environment": settings.environment}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": str(exc) if settings.debug else "An error occurred", "type": type(exc).__name__}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug, timeout_keep_alive=120)
