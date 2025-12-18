"""
FastAPI application entry point for the Agent Control Plane.

This module creates the FastAPI application, configures middleware,
and includes all API routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agent
from app.config import settings

app = FastAPI(
    title="Agent Control Plane",
    description="Agent orchestration service using LangGraph",
    version="0.1.0",
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url="/redoc" if settings.app_env == "development" else None,
)

# CORS middleware - configure for your specific requirements
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent.router, prefix="/agent", tags=["agent"])


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        A dictionary indicating the service is healthy.
    """
    return {"status": "healthy"}


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """
    Root endpoint.

    Returns:
        Basic service information.
    """
    return {
        "service": "Agent Control Plane",
        "version": "0.1.0",
        "docs": "/docs" if settings.app_env == "development" else "disabled",
    }

