from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.core.constants import ErrorMsg
from app.models.bookmark import Bookmark
from app.models.user import User
from app.schemas.opportunity import OpportunitySavePayload
from app.schemas.response import APIResponse, error_response, success_response
from app.services.bookmark_service import BookmarkService
from app.services.opportunity_service import OpportunityService

router = APIRouter()


@router.get("/", response_model=APIResponse)
def list_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BookmarkService(db)
    bookmarks = service.get_user_bookmarks(current_user.id)
    return success_response(
        "Bookmarks retrieved successfully.",
        data={"count": len(bookmarks), "bookmarks": bookmarks},
    )


@router.post("/{opportunity_id}", response_model=APIResponse)
def add_bookmark(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BookmarkService(db)
    if service.repository.bookmark_exists(current_user.id, opportunity_id):
        return error_response("Opportunity already bookmarked.")

    bookmark = Bookmark(user_id=current_user.id, opportunity_id=opportunity_id)
    created = service.create(bookmark)
    return success_response("Opportunity bookmarked successfully.", data={"id": created.id})


@router.delete("/{opportunity_id}", response_model=APIResponse)
def remove_bookmark(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = BookmarkService(db)
    if not service.repository.bookmark_exists(current_user.id, opportunity_id):
        return error_response(ErrorMsg.OPPORTUNITY_NOT_FOUND.value)

    service.repository.remove_bookmark(current_user.id, opportunity_id)
    return success_response("Bookmark removed successfully.")


@router.post("/save", response_model=APIResponse)
def save_and_bookmark(
    payload: OpportunitySavePayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bookmarks a live opportunity (from /opportunities/search,
    /recommendations, /hackathons/search or /research/search) that has no
    DB id yet -- upserts it into the opportunities table (by apply_link)
    then bookmarks that row. This is what the frontend calls; the
    id-based endpoints above stay as-is for already-persisted rows."""
    opportunity_service = OpportunityService(db)
    bookmark_service = BookmarkService(db)

    try:
        opportunity = opportunity_service.get_or_create_from_payload(payload.model_dump())
    except ValueError as e:
        return error_response(str(e))

    if bookmark_service.repository.bookmark_exists(current_user.id, opportunity.id):
        return success_response("Already bookmarked.", data={"id": opportunity.id, "already_bookmarked": True})

    bookmark = Bookmark(user_id=current_user.id, opportunity_id=opportunity.id)
    bookmark_service.create(bookmark)
    return success_response("Opportunity bookmarked successfully.", data={"id": opportunity.id})


@router.get("/detailed", response_model=APIResponse)
def list_bookmarks_detailed(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Same data as GET /bookmarks/, but flattened into plain dicts
    (title, company, apply_link, etc.) so the frontend can render cards
    without needing to know the SQLAlchemy relationship shape."""
    service = BookmarkService(db)
    bookmarks = service.get_user_bookmarks(current_user.id)

    items = []
    for b in bookmarks:
        opp = b.opportunity
        items.append({
            "bookmark_id": b.id,
            "opportunity_id": opp.id if opp else b.opportunity_id,
            "title": opp.title if opp else "",
            "company": opp.company if opp else "",
            "location": opp.location if opp else "",
            "salary": opp.salary if opp else "",
            "deadline": str(opp.deadline) if opp and opp.deadline else "",
            "apply_link": opp.apply_link if opp else "",
            "description": opp.description if opp else "",
            "skills": opp.skills if opp else "",
            "source": opp.source if opp else "",
            "type": opp.opportunity_type if opp else "",
            "created_at": str(b.created_at) if b.created_at else "",
        })

    return success_response(
        "Bookmarks retrieved successfully.",
        data={"count": len(items), "bookmarks": items},
    )
