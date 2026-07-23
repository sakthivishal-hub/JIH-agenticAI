"""
Application lifespan management for OpportunityOS.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.ai.search_agent import search_agent
from app.providers.live_providers import register_live_providers
from app.services.notification_scheduler import start_scheduler, stop_scheduler

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

    # Provider registration -- gives the search agent real, live sources
    # instead of an empty provider list.
    if not search_agent.providers:
        register_live_providers(search_agent)

    # Scheduler startup -- periodic email/WhatsApp notification job.
    start_scheduler()

    yield

    stop_scheduler()

    logger.info("=" * 60)
    logger.info("Shutting down OpportunityOS...")
    logger.info("Cleanup completed.")
    logger.info("=" * 60)