"""
BWW Assistant FastAPI Server
Main FastAPI application with lifecycle management
"""

from typing import Any, Dict

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path

from config.logging_config import setup_logging, get_logger
from config.settings import settings
from database import create_all_tables
from Server.routes import dashboard, api, webhook, settings_api

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    try:
        # Create database tables
        create_all_tables()
        logger.info("Database initialized successfully")

        # Initialize all services using the new modular architecture
        try:
            from app.services.bootstrap import initialize_services, get_service_bootstrap
            if initialize_services():
                service_bootstrap = get_service_bootstrap()
                logger.info("Modular service architecture initialized successfully")
                app.state.service_bootstrap = service_bootstrap
            else:
                logger.warning("Service bootstrap initialization failed")
        except Exception as e:
            logger.error(f"Service bootstrap failed: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Don't let startup errors crash the app
        pass

    yield

    # Shutdown
    try:
        # Shutdown all services using the modular architecture
        try:
            if hasattr(app.state, 'service_bootstrap') and app.state.service_bootstrap:
                from app.services.bootstrap import shutdown_services
                shutdown_services()
                logger.info("Modular service architecture shutdown successfully")
        except Exception as e:
            logger.warning(f"Service shutdown failed: {e}")
    except Exception as e:
        logger.warning(f"Error during shutdown: {e}")

# Create FastAPI app
app = FastAPI(
    title="BWW Assistant - Facebook Messenger Platform",
    description="A professional Facebook Messenger bot platform with AI integration",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files from app/static (services are still in app/)
project_root = Path(__file__).parent.parent
static_dir = project_root / "app" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"Static files mounted from: {static_dir}")

# Setup templates from app/templates (services are still in app/)
templates_dir = project_root / "app" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))
logger.info(f"Templates configured from: {templates_dir}")

# Include routers
app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(api.router, prefix="/api", tags=["api"])
app.include_router(settings_api.router, tags=["settings-api"])  # Settings API endpoints


@app.get("/")
async def root():
    """Root endpoint - redirect to dashboard"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard", status_code=302)


@app.get("/health")
async def health_check():
    """Health check endpoint with service status"""
    try:
        health_status = {"status": "healthy", "service": "bww-ai-assistant"}

        # Check service bootstrap health if available
        if hasattr(app.state, 'service_bootstrap') and app.state.service_bootstrap:
            try:
                service_health = app.state.service_bootstrap.health_check()
                health_status["services"] = service_health
            except Exception as e:
                health_status["service_error"] = str(e)

        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


@app.get("/info")
async def server_info() -> Dict[str, Any]:
    """Server information endpoint"""
    return {
        "name": "BWW Assistant Server",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "facebook_app_id": settings.FB_APP_ID,
        "database_url": settings.DATABASE_URL,
        "documentation": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    uvicorn.run(
        "Server.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
