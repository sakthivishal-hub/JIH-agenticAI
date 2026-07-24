"""
Notification service for OpportunityOS.

Sends automated email and WhatsApp alerts about new/matched opportunities.
Email uses plain smtplib against the SMTP_* settings; WhatsApp uses the
Twilio REST API (no SDK dependency needed -- a couple of HTTP calls).

Both channels degrade gracefully: if credentials aren't configured, the
call is logged and skipped rather than raising, so the rest of the app
(and any request that triggered a notification) keeps working even on a
fresh checkout with an empty .env.
"""
from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationError(Exception):
    """Raised only for caller-facing failures (e.g. explicit test send)."""


def _email_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD)


def _whatsapp_configured() -> bool:
    return bool(
        settings.TWILIO_ACCOUNT_SID
        and settings.TWILIO_AUTH_TOKEN
        and settings.TWILIO_WHATSAPP_FROM
    )


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Sends a plain-text email. Returns True on success, False if
    unconfigured or on failure (logged either way, never raises)."""
    if not _email_configured():
        logger.info("Email not configured (SMTP_* missing) -- skipping send to %s", to_email)
        return False

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM or settings.SMTP_USERNAME
    message["To"] = to_email

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(message["From"], [to_email], message.as_string())
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False


async def send_whatsapp(to_number: str, body: str) -> bool:
    """Sends a WhatsApp message via the Twilio REST API. Returns True on
    success, False if unconfigured or on failure (never raises)."""
    if not _whatsapp_configured():
        logger.info("WhatsApp not configured (TWILIO_* missing) -- skipping send to %s", to_number)
        return False

    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
    to = to_number if to_number.startswith("whatsapp:") else f"whatsapp:{to_number}"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                url,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                data={"From": settings.TWILIO_WHATSAPP_FROM, "To": to, "Body": body},
            )
            response.raise_for_status()
        return True
    except Exception:
        logger.exception("Failed to send WhatsApp message to %s", to_number)
        return False


def format_opportunity_digest(opportunities: list[dict[str, Any]], *, max_items: int = 5) -> str:
    """Formats a short human-readable digest shared by both channels."""
    if not opportunities:
        return "No new matching opportunities right now -- check back soon."

    lines = ["New opportunities matched for you:\n"]
    for opp in opportunities[:max_items]:
        title = opp.get("title", "Untitled opportunity")
        company = opp.get("company", "")
        link = opp.get("apply_link", "")
        score = opp.get("overall_score")
        score_tag = f" ({score}% match)" if score is not None else ""
        lines.append(f"- {title} at {company}{score_tag}\n  {link}")
    return "\n".join(lines)


async def notify_user(
    user,
    opportunities: list[dict[str, Any]],
    *,
    subject: str = "OpportunityOS: New matches for you",
) -> dict[str, bool]:
    """Sends the opportunity digest to a user on every channel they've
    opted into. Returns which channels actually succeeded."""
    body = format_opportunity_digest(opportunities)
    results = {"email": False, "whatsapp": False}

    if getattr(user, "notify_email", False) and getattr(user, "email", None):
        results["email"] = send_email(user.email, subject, body)

    if getattr(user, "notify_whatsapp", False) and getattr(user, "whatsapp_number", None):
        results["whatsapp"] = await send_whatsapp(user.whatsapp_number, body)

    return results
