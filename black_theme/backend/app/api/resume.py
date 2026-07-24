import logging
import tempfile
from pathlib import Path
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, File, UploadFile

from app.ai.resume_parser import resume_parser, ResumeParserError
from app.api.deps import get_current_user
from app.core.constants import ErrorMsg, SuccessMsg
from app.core.validator import validate_resume
from app.models.user import User
from app.schemas.response import APIResponse, error_response, success_response
from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

_CHUNK_SIZE = 1024 * 1024  # 1MB, for streamed size checking


@router.post("/upload", response_model=APIResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
):
    if not file.filename:
        return error_response(ErrorMsg.INVALID_FILE_TYPE.value)

    # Read the file into memory once -- needed for both the magic-byte
    # signature check and the size check, and to avoid trusting the
    # client-reported Content-Length header.
    content = await file.read()
    file_head = content[:16]

    ok, reason = validate_resume(
        filename=file.filename,
        content_type=file.content_type or "",
        file_size=len(content),
        file_head=file_head,
    )
    if not ok:
        return error_response(reason)

    suffix = Path(file.filename).suffix.lower()
    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(content)
            temp_path = temp.name

        resume_data = await resume_parser.aparse(temp_path)

    except ResumeParserError as exc:
        # Bad/unreadable resume content is a client-facing problem (422),
        # not a server failure -- and we don't leak internal exception
        # details, just the parser's own message.
        logger.warning("Resume parse failed for user_id=%s: %s", current_user.id, exc)
        return error_response(str(exc))

    except Exception:
        logger.exception("Unexpected error parsing resume for user_id=%s", current_user.id)
        return error_response(ErrorMsg.SERVER_ERROR.value)

    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)

    # Persist so the recommender has something to work with later --
    # this was the step the original version skipped entirely.
    current_user.resume_text = str(resume_data)
    current_user.skills = resume_data.get("skills", [])
    session.add(current_user)
    session.commit()

    return success_response(SuccessMsg.RESUME_UPLOADED.value, data=resume_data)