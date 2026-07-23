import logging

from fastapi import APIRouter, Query

from app.ai.search_agent import search_agent, SearchAgentError
from app.core.constants import ErrorMsg, SuccessMsg
from app.schemas.response import APIResponse, error_response, success_response

logger = logging.getLogger(__name__)
router = APIRouter()

_MAX_LIMIT = 50
_MAX_QUERY_LENGTH = 200


@router.get("/search", response_model=APIResponse)
async def search(
    query: str = Query(..., min_length=1, max_length=_MAX_QUERY_LENGTH),
    location: str | None = Query(None, max_length=100),
    limit: int = Query(20, ge=1, le=_MAX_LIMIT),
):
    query = query.strip()
    if not query:
        return error_response(ErrorMsg.VALIDATION_ERROR.value)

    try:
        results = await search_agent.search(query=query, location=location, limit=limit)
    except SearchAgentError as exc:
        logger.warning("Search failed for query=%r: %s", query, exc)
        return error_response(ErrorMsg.SERVER_ERROR.value)
    except Exception:
        logger.exception("Unexpected error during search, query=%r", query)
        return error_response(ErrorMsg.SERVER_ERROR.value)

    return success_response(
        SuccessMsg.OPPORTUNITY_FOUND.value,
        data={"count": len(results), "results": results},
    )