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
from app.config import settings
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.sentinel_service import SentinelService
from app.services.oracle_service import OracleService
from app.workers.news_monitor_worker import NewsMonitorWorker
from app.workers.competitor_tracker_worker import CompetitorTrackerWorker
from app.workers.trend_spotter_worker import TrendSpotterWorker
import logging

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
    context, clients, social_accounts, brand_files, content_lab, calendar, agents,
    system, omega, nova, sentinel, oracle, prompt_vault, handoff, reseller, upsell, admin, sub_brands
)
# DEBT-036: legacy Lovable billing module desregistrado · reemplazado por billing_v3 bc_billing
from app.api.routes import billing_v3
from app.api.routes import aria_v1
from app.api.routes import clients_v3
from app.api.routes import content_v3
from app.api.routes import calendar_v3
from app.api.routes import content_lab_v3
from app.sentinel.persistence_router import router as sentinel_persistence_router
from app.api.routes.clients.feature_usage_router import router as feature_usage_router

# Services & scheduler
sentinel_service = SentinelService()
oracle_service = OracleService()
scheduler = AsyncIOScheduler(timezone="America/Puerto_Rico")

# Create FastAPI application
app = FastAPI(
    title="OmegaRaisen API", version="2.0.0",
    description="Social Media Automation — 37 AI Agents | Enterprise Platform",
    docs_url="/docs", redoc_url="/redoc",
)

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
    # SENTINEL cron jobs
    scheduler.add_job(sentinel_service.run_vault_scan, 'cron', hour=2, minute=0, id='vault_scan')
    scheduler.add_job(sentinel_service.run_db_guardian, 'cron', hour=5, minute=0, id='db_guardian')
    scheduler.add_job(sentinel_service.run_full_scan, 'cron', hour=7, minute=0, id='sentinel_brief')
    scheduler.add_job(sentinel_service.run_pulse_monitor, 'interval', minutes=5, id='pulse_monitor')
    # ORACLE cron jobs
    scheduler.add_job(oracle_service.generate_intelligence_brief, 'cron', day_of_week='mon', hour=7, minute=0, id='oracle_weekly_brief')
    # OMEGA Workers v2
    news_worker = NewsMonitorWorker()
    scheduler.add_job(news_worker.run_all_clients, 'interval', hours=2, id='news_monitor', max_instances=1)
    competitor_worker = CompetitorTrackerWorker()
    scheduler.add_job(competitor_worker.run_all_clients, 'interval', hours=6, id='competitor_tracker', max_instances=1)
    trend_worker = TrendSpotterWorker()
    scheduler.add_job(trend_worker.run_all_clients, 'interval', hours=12, id='trend_spotter', max_instances=1)
    # BRAND DNA refresh (DEBT-044 Sprint 2 · 9no cron job)
    from app.bc_cognition.application.use_brand_dna import refresh_all_brand_dna
    scheduler.add_job(refresh_all_brand_dna, 'cron', hour=3, minute=0, id='brand_dna_refresh')
    scheduler.start()
    logger.info("✅ SENTINEL + ORACLE + OMEGA + BRAND_DNA workers activos — 9 jobs registrados")

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
app.include_router(aria_v1.router, prefix=settings.api_v1_prefix, tags=["ARIA"])
app.include_router(clients_v3.router, prefix=settings.api_v1_prefix, tags=["Clients V3"])
app.include_router(content_v3.router, prefix=settings.api_v1_prefix, tags=["Content V3"])
app.include_router(calendar_v3.router, prefix=settings.api_v1_prefix, tags=["Calendar V3"])
app.include_router(content_lab_v3.router, prefix=settings.api_v1_prefix, tags=["Content Lab V3"])
app.include_router(context.router, prefix=settings.api_v1_prefix)
app.include_router(clients.router, prefix=settings.api_v1_prefix, tags=["Clients 👥"])
app.include_router(social_accounts.router, prefix=settings.api_v1_prefix, tags=["Social Accounts 📱"])
app.include_router(brand_files.router, prefix=settings.api_v1_prefix, tags=["Brand Files 📎"])
app.include_router(content_lab.router, prefix=settings.api_v1_prefix, tags=["Content Lab 🎨"])
app.include_router(calendar.router, prefix=settings.api_v1_prefix, tags=["Calendar 📅"])
app.include_router(agents.router, prefix=settings.api_v1_prefix, tags=["Agents 🤖"])
app.include_router(system.router, prefix=settings.api_v1_prefix, tags=["System 🔧"])
app.include_router(omega.router, prefix=settings.api_v1_prefix, tags=["OMEGA Company 👑"])
app.include_router(nova.router, prefix=settings.api_v1_prefix, tags=["NOVA 👑"])
app.include_router(sentinel.router, prefix=settings.api_v1_prefix, tags=["SENTINEL 🛡️"])
app.include_router(sentinel_persistence_router)
app.include_router(oracle.router, prefix=settings.api_v1_prefix + "/oracle", tags=["ORACLE 🔮"])
app.include_router(prompt_vault.router, prefix=settings.api_v1_prefix, tags=["Prompt Vault 📚"])
app.include_router(handoff.router, prefix=settings.api_v1_prefix, tags=["Handoff Protocol 🤝"])
app.include_router(reseller.router, prefix=settings.api_v1_prefix, tags=["Reseller Dashboard 🏢"])
app.include_router(upsell.router, prefix=settings.api_v1_prefix, tags=["Upsell 💰"])
app.include_router(admin.router, prefix=settings.api_v1_prefix, tags=["Admin Panel ⚙️"])
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
    return {"status": "healthy", "version": "2.0.0", "agents": f"{total_agents}/{total_agents}", "environment": settings.environment}

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
