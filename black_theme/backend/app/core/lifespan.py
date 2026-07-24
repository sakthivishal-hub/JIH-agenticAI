"""
Application lifespan management for OpportunityOS.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    logger.info("=" * 60)
    logger.info("Starting OpportunityOS...")
    logger.info("Initializing application...")
    logger.info("=" * 60)

    # Future startup tasks
    #
    # Database initialization
    # Cache initialization
    # AI model loading
    # Provider registration
    # Scheduler startup

    yield

    logger.info("=" * 60)
    logger.info("Shutting down OpportunityOS...")
    logger.info("Cleanup completed.")
    logger.info("=" * 60)