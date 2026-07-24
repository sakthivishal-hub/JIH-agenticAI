"""
Automated notification scheduler for OpportunityOS.

Runs a background job every JOB_REFRESH_HOURS (see .env) that looks at
every user who has opted into email or WhatsApp notifications, runs a
lightweight keyword search against the live providers using their
preferred_role/skills, and sends a digest of new opportunities.

Deliberately keyword-based rather than the full Gemini matcher pipeline
(app/ai/recommender.py) -- this job can run for every opted-in user on a
timer, and re-running the LLM matcher for all of them on every tick would
burn API quota fast. The full AI-scored recommendations are still
available on-demand via POST /recommendations.
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.ai.search_agent import search_agent
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.services.notification_service import notify_user

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _run_notification_sweep() -> None:
    db = SessionLocal()
    try:
        users = (
            db.query(User)
            .filter(User.is_active == True)  # noqa: E712
            .filter((User.notify_email == True) | (User.notify_whatsapp == True))  # noqa: E712
            .all()
        )
        if not users:
            return

        logger.info("Notification sweep: checking %d opted-in user(s)", len(users))

        for user in users:
            query = user.preferred_role or user.skills or user.interests
            if not query:
                continue
            try:
                opportunities = await search_agent.search(
                    query=query, location=user.preferred_location, limit=5
                )
                if not opportunities:
                    continue
                results = await notify_user(user, opportunities)
                logger.info(
                    "Notified user_id=%s email=%s whatsapp=%s",
                    user.id, results.get("email"), results.get("whatsapp"),
                )
            except Exception:
                logger.exception("Notification sweep failed for user_id=%s", user.id)
    finally:
        db.close()


def start_scheduler() -> None:
    """Starts the background scheduler. Safe to call multiple times."""
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _run_notification_sweep,
        "interval",
        hours=max(settings.JOB_REFRESH_HOURS, 1),
        id="opportunity_notification_sweep",
    )
    _scheduler.start()
    logger.info(
        "Notification scheduler started (interval=%sh)", settings.JOB_REFRESH_HOURS
    )


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
