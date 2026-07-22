"""
AI Resume Parser.
Pipeline:
PDF/DOCX
    ↓
Extract Text
    ↓
Clean Text
    ↓
Gemini
    ↓
JSON
"""
from __future__ import annotations

import logging
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document  # python-docx

from app.ai.llm import llm, LLMError
from app.ai.prompts import resume_parser_prompt

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {
    "full_name", "email", "phone", "location", "linkedin", "github",
    "portfolio", "summary", "education", "experience", "projects",
    "skills", "certifications", "languages",
}
_LIST_KEYS = {"education", "experience", "projects", "skills", "certifications", "languages"}


class ResumeParserError(Exception):
    """Raised when resume parsing fails."""


class ResumeParser:
    MAX_CHARACTERS = 30_000
    MAX_PAGES = 15  # resumes are short; caps runaway/malicious uploads

    # ---------------------------------------------------------------
    # Text extraction
    # ---------------------------------------------------------------
    @classmethod
    def extract_text(cls, file_path: str) -> str:
        """Extract text from a PDF or DOCX file, based on extension."""
        suffix = Path(file_path).suffix.lower()
        if suffix == ".pdf":
            return cls._extract_pdf(file_path)
        if suffix == ".docx":
            return cls._extract_docx(file_path)
        raise ResumeParserError(
            f"Unsupported file type for parsing: {suffix}. "
            f"Only .pdf and .docx are supported."
        )

    @classmethod
    def _extract_pdf(cls, pdf_path: str) -> str:
        try:
            document = fitz.open(pdf_path)
        except Exception as exc:
            raise ResumeParserError(f"Unable to open PDF: {exc}") from exc

        try:
            if document.page_count > cls.MAX_PAGES:
                raise ResumeParserError(
                    f"PDF has {document.page_count} pages; resumes should be "
                    f"under {cls.MAX_PAGES}. Rejecting to avoid a bad upload."
                )
            pages = [page.get_text() for page in document]
        except ResumeParserError:
            raise
        except Exception as exc:
            raise ResumeParserError(f"Unable to read PDF content: {exc}") from exc
        finally:
            document.close()  # always runs, even if extraction fails mid-loop

        text = "\n".join(pages)
        if not text.strip():
            # Most common cause: scanned/image-only PDF with no text layer.
            raise ResumeParserError(
                "No text found in PDF. This usually means the file is a "
                "scanned image rather than a text-based PDF -- OCR isn't "
                "supported yet, please upload a text-based PDF or DOCX."
            )
        return text

    @staticmethod
    def _extract_docx(docx_path: str) -> str:
        try:
            doc = Document(docx_path)
        except Exception as exc:
            raise ResumeParserError(f"Unable to open DOCX: {exc}") from exc

        text = "\n".join(p.text for p in doc.paragraphs)
        if not text.strip():
            raise ResumeParserError("No text found in DOCX file.")
        return text

    # ---------------------------------------------------------------
    # Cleaning
    # ---------------------------------------------------------------
    @classmethod
    def clean_text(cls, text: str) -> str:
        """Normalize whitespace and cap length."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned = "\n".join(lines)
        if len(cleaned) > cls.MAX_CHARACTERS:
            logger.warning("Resume text truncated from %d to %d chars", len(cleaned), cls.MAX_CHARACTERS)
            cleaned = cleaned[: cls.MAX_CHARACTERS]
        return cleaned

    # ---------------------------------------------------------------
    # Schema safety net
    # ---------------------------------------------------------------
    @staticmethod
    def _normalize_schema(data: dict) -> dict:
        """Fills in any keys the model dropped, so downstream code
        (matcher, profile save) never has to defensively check for
        missing keys."""
        for key in _REQUIRED_KEYS:
            if key not in data or data[key] is None:
                data[key] = [] if key in _LIST_KEYS else ""
        return data

    # ---------------------------------------------------------------
    # Public entrypoints
    # ---------------------------------------------------------------
    @classmethod
    def parse(cls, file_path: str) -> dict:
        """Synchronous parse. Use `aparse` inside async route handlers."""
        text = cls.clean_text(cls.extract_text(file_path))
        prompt = resume_parser_prompt(text)
        try:
            data = llm.generate_json(prompt)
        except LLMError as exc:
            raise ResumeParserError(f"AI parsing failed: {exc}") from exc
        return cls._normalize_schema(data)

    @classmethod
    async def aparse(cls, file_path: str) -> dict:
        """Async parse for use inside FastAPI async routes -- runs PDF/DOCX
        extraction (blocking, CPU-bound) and the LLM call in a thread so
        neither stalls the event loop."""
        import asyncio
        return await asyncio.to_thread(cls.parse, file_path)


resume_parser = ResumeParser