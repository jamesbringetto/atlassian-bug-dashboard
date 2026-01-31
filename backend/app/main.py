"""
Main FastAPI application for Atlassian Cloud Migration Bug Dashboard.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import bugs, analytics, health

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Atlassian Cloud Migration Bug Dashboard API")
    logger.info(f"Creating database tables if they don't exist")
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    logger.info("Shutting down Atlassian Cloud Migration Bug Dashboard API")


# Create FastAPI app
app = FastAPI(
    title="Atlassian Cloud Migration Bug Dashboard API",
    description="REST API for analyzing Atlassian's public bug data",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(bugs.router, prefix="/api", tags=["bugs"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Atlassian Cloud Migration Bug Dashboard API",
        "version": "0.1.0",
        "docs": "/docs"
    }
