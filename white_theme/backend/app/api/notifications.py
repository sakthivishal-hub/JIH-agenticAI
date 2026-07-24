import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.core.constants import SuccessMsg
from app.models.user import User
from app.schemas.notification import NotificationPreferencesRequest, NotificationPreferencesResponse
from app.schemas.response import APIResponse, error_response, success_response
from app.services.notification_service import notify_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/preferences", response_model=NotificationPreferencesResponse)
def get_preferences(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/preferences", response_model=NotificationPreferencesResponse)
def update_preferences(
    request: NotificationPreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if request.notify_email is not None:
        current_user.notify_email = request.notify_email
    if request.notify_whatsapp is not None:
        current_user.notify_whatsapp = request.notify_whatsapp
    if request.whatsapp_number is not None:
        current_user.whatsapp_number = request.whatsapp_number

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/test", response_model=APIResponse)
async def send_test_notification(current_user: User = Depends(get_current_user)):
    """Sends a sample opportunity digest on every channel the user has
    opted into -- lets the frontend verify SMTP/Twilio setup immediately
    instead of waiting for the next scheduled sweep."""
    sample = [{
        "title": "Sample Opportunity",
        "company": "OpportunityOS",
        "apply_link": "https://example.com",
        "overall_score": 92,
    }]

    results = await notify_user(current_user, sample, subject="OpportunityOS: Test notification")

    if not results["email"] and not results["whatsapp"]:
        return error_response(
            "No notification channel is configured or enabled. "
            "Check your preferences and the server's SMTP/Twilio settings."
        )

    return success_response(SuccessMsg.NOTIFICATION_SENT.value, data=results)
