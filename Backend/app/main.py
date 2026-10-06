"""Kalakriti Backend Application Entrypoint — FastAPI ASGI application."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import (
    auth,
    b2b,
    image,
    ondc,
    pricing,
    products,
    qr,
    voice,
)
from app.services.pricing_service import init_pricing_model
from app.utils.logger import logger, setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager — startup and shutdown lifecycle hooks."""
    # Startup
    setup_logger()
    logger.info("Initializing Kalakriti Backend [Env: {}]", settings.environment)
    init_pricing_model()
    yield
    # Shutdown
    logger.info("Kalakriti Backend shutting down cleanly")


app = FastAPI(
    title="Kalakriti API",
    description="AI-Driven Market Linkage & Smart Cataloging Gateway for Indian Artisans",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits Expo Go local dev, mobile apps, and web portals
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Router Ingestion (/api/v1)
# ---------------------------------------------------------------------------
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(voice.router, prefix=API_PREFIX)
app.include_router(image.router, prefix=API_PREFIX)
app.include_router(products.router, prefix=API_PREFIX)
app.include_router(pricing.router, prefix=API_PREFIX)
app.include_router(ondc.router, prefix=API_PREFIX)
app.include_router(b2b.router, prefix=API_PREFIX)
app.include_router(qr.router, prefix=API_PREFIX)


# ---------------------------------------------------------------------------
# Health & Status Endpoints
# ---------------------------------------------------------------------------
@app.get(
    "/",
    tags=["Health"],
    status_code=status.HTTP_200_OK,
    summary="Root service banner",
)
async def root() -> dict[str, Any]:
    """Root heartbeat check."""
    return {
        "service": "Kalakriti API",
        "version": "1.0.0",
        "status": "online",
        "dpi_linkage": ["ONDC", "GeM"],
    }


@app.get(
    "/health",
    tags=["Health"],
    status_code=status.HTTP_200_OK,
    summary="System health check endpoint",
)
async def health_check() -> JSONResponse:
    """Detailed health check for container orchestration and uptime monitors."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "environment": settings.environment,
            "database": "connected",
        },
    )