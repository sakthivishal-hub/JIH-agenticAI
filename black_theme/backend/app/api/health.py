"""
Health check endpoints for OpportunityOS.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/")
async def health():
    """
    Application health endpoint.
    """

    return {
        "success": True,
        "status": "healthy",
        "service": "OpportunityOS",
        "version": "1.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint.
    """

    return {
        "message": "pong",
    }


@router.get("/ready")
async def readiness():
    """
    Readiness endpoint.
    """

    return {
        "ready": True,
    }