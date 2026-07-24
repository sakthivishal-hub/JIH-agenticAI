from pathlib import Path

from app.core.constants import (
    ALLOWED_RESUME_EXTENSIONS,
    ALLOWED_RESUME_MIME_TYPES,
    MAX_RESUME_SIZE_BYTES,
    ErrorMsg,
)

# Magic-byte signatures for the file types we accept. Content-Type headers
# are client-supplied and trivially spoofable, so we sniff actual bytes as
# the source of truth; the declared MIME type is only a secondary check.
_PDF_SIGNATURE = b"%PDF-"
_ZIP_SIGNATURE = b"PK\x03\x04"          # .docx (zip-based)
_OLE_SIGNATURE = b"\xd0\xcf\x11\xe0"    # legacy .doc (OLE compound file)


def validate_resume_extension(filename: str) -> bool:
    """Validate file extension."""
    return Path(filename).suffix.lower() in ALLOWED_RESUME_EXTENSIONS


def validate_resume_mime(content_type: str) -> bool:
    """Validate client-declared MIME type. Secondary check only -- see
    validate_resume_signature for the check that actually matters."""
    return content_type in ALLOWED_RESUME_MIME_TYPES


def validate_resume_signature(file_head: bytes) -> bool:
    """Validate the file's actual magic bytes. This is the check that
    can't be spoofed by renaming a file or setting a fake Content-Type."""
    return file_head.startswith(_PDF_SIGNATURE) or file_head.startswith(
        (_ZIP_SIGNATURE, _OLE_SIGNATURE)
    )


def validate_resume_size(file_size: int) -> bool:
    """Validate uploaded file size (rejects empty files too)."""
    return 0 < file_size <= MAX_RESUME_SIZE_BYTES


def validate_filename_safety(filename: str) -> bool:
    """Rejects path traversal / null-byte tricks in the filename before
    it's ever used to build a save path."""
    if not filename or "\x00" in filename:
        return False
    return Path(filename).name == filename  # no ../ or / components


def validate_resume(
    filename: str,
    content_type: str,
    file_size: int,
    file_head: bytes = b"",
) -> tuple[bool, str]:
    """
    Validate an uploaded resume.

    file_head: first ~16 bytes of the file content, used for magic-byte
    signature checking. Pass this in from the upload handler
    (e.g. `await file.read(16)`, then seek back to 0).

    Returns:
        (True, "Valid") if the resume passes all checks.
        (False, reason) otherwise, reason is an ErrorMsg value.
    """
    if not validate_filename_safety(filename):
        return False, ErrorMsg.INVALID_FILE_TYPE.value

    if not validate_resume_extension(filename):
        return False, ErrorMsg.INVALID_FILE_TYPE.value

    if not validate_resume_mime(content_type):
        return False, ErrorMsg.INVALID_FILE_TYPE.value

    if not validate_resume_size(file_size):
        return False, ErrorMsg.FILE_TOO_LARGE.value

    if file_head and not validate_resume_signature(file_head):
        return False, ErrorMsg.INVALID_FILE_TYPE.value

    return True, "Valid"