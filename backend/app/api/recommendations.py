import logging

from fastapi import APIRouter, Depends, Query

from app.ai.recommender import recommender, RecommendationError
from app.ai.search_agent import search_agent, SearchAgentError
from app.ai.llm import LLMError
from app.api.deps import get_current_user
from app.core.constants import ErrorMsg, SuccessMsg
from app.models.user import User
from app.schemas.response import APIResponse, error_response, success_response

logger = logging.getLogger(__name__)
router = APIRouter()

_MAX_QUERY_LENGTH = 200
_MAX_TOP_K = 20
_SEARCH_POOL_SIZE = 30  # how many candidate opportunities to fetch before ranking


@router.post("/", response_model=APIResponse)
async def recommend(
    query: str = Query(..., min_length=1, max_length=_MAX_QUERY_LENGTH),
    location: str | None = Query(None, max_length=100),
    top_k: int = Query(10, ge=1, le=_MAX_TOP_K),
    current_user: User = Depends(get_current_user),
):
    query = query.strip()
    if not query:
        return error_response(ErrorMsg.VALIDATION_ERROR.value)

    if not current_user.resume_text:
        return error_response(
            "No resume on file. Upload a resume via /resume/upload before requesting recommendations."
        )

    try:
        opportunities = await search_agent.search(
            query=query, location=location, limit=_SEARCH_POOL_SIZE
        )
    except SearchAgentError as exc:
        logger.warning("Search failed for user_id=%s query=%r: %s", current_user.id, query, exc)
        return error_response(ErrorMsg.SERVER_ERROR.value)

    if not opportunities:
        return success_response(
            SuccessMsg.OPPORTUNITY_FOUND.value, data={"count": 0, "recommendations": []}
        )

    try:
        recommendations = await recommender.arecommend(
            resume=current_user.resume_text,  # the user's own verified, parsed resume -- never client-supplied
            opportunities=opportunities,
            top_k=top_k,
        )
    except (RecommendationError, LLMError) as exc:
        logger.warning("Recommendation failed for user_id=%s: %s", current_user.id, exc)
        return error_response(ErrorMsg.SERVER_ERROR.value)
    except Exception:
        logger.exception("Unexpected error generating recommendations for user_id=%s", current_user.id)
        return error_response(ErrorMsg.SERVER_ERROR.value)

    return success_response(
        SuccessMsg.MATCHES_COMPUTED.value,
        data={"count": len(recommendations), "recommendations": recommendations},
    )