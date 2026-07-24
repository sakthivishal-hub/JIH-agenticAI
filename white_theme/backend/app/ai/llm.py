"""
Centralized Gemini LLM client for OpportunityOS.
Every AI module should use this client instead of creating its own.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import re
from typing import Any

from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.ai.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)
_RETRYABLE_CODES = {429, 500, 502, 503, 504}
_REQUEST_TIMEOUT_MS = 30_000


class LLMError(Exception):
    """Permanent failure -- do not retry. Safe to surface to the caller."""


class LLMTransientError(LLMError):
    """Retryable failure: rate limit, server error, or empty/truncated output."""


class LLMSafetyBlockedError(LLMError):
    """The model refused to generate content for this prompt."""


def _prompt_fingerprint(prompt: str) -> str:
    """Short hash for log correlation without leaking prompt content
    (prompts may contain resume/PII data)."""
    return hashlib.sha256(prompt.encode()).hexdigest()[:12]


class GeminiClient:
    """
    Singleton Gemini client.
    Usage:
        llm = GeminiClient()
        text = llm.generate(prompt)
        data = llm.generate_json(prompt)
        data = await llm.agenerate_json(prompt)   # for use inside async routes
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise LLMError(
                "GEMINI_API_KEY is not set. Add it to your .env before starting the app."
            )
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

    @staticmethod
    def _strip_fences(text: str) -> str:
        return _FENCE_RE.sub("", text).strip()

    def _call(
        self,
        prompt: str,
        *,
        temperature: float,
        max_output_tokens: int,
        system_instruction: str | None,
    ) -> str:
        """Single API call with proper error classification. Raises
        LLMTransientError only for genuinely retryable conditions;
        everything else raises LLMError/LLMSafetyBlockedError immediately."""
        fp = _prompt_fingerprint(prompt)
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    system_instruction=system_instruction,
                    http_options=types.HttpOptions(timeout=_REQUEST_TIMEOUT_MS),
                ),
            )
        except genai_errors.APIError as exc:
            code = getattr(exc, "code", None)
            logger.warning("Gemini API error [prompt=%s] code=%s: %s", fp, code, exc)
            if code in _RETRYABLE_CODES:
                raise LLMTransientError(f"Gemini API error (code={code})") from exc
            raise LLMError(f"Gemini API error (code={code}): {exc}") from exc
        except Exception as exc:
            # Network-level failures (timeout, connection reset) land here --
            # these ARE worth retrying.
            logger.warning("Gemini call failed [prompt=%s]: %s", fp, exc)
            raise LLMTransientError(str(exc)) from exc

        candidate = (response.candidates or [None])[0]
        finish_reason = getattr(candidate, "finish_reason", None)
        if finish_reason and str(finish_reason).upper() in {"SAFETY", "PROHIBITED_CONTENT"}:
            raise LLMSafetyBlockedError(
                f"Gemini declined to generate content (finish_reason={finish_reason})"
            )

        text = (response.text or "").strip()
        if not text:
            raise LLMTransientError("Empty response from Gemini.")
        return text

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(LLMTransientError),
        reraise=True,
    )
    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_output_tokens: int = 4096,
        system_instruction: str | None = SYSTEM_PROMPT,
    ) -> str:
        """Generate plain text. Only retries rate limits / server errors /
        network blips / empty output -- auth and bad-request errors fail fast."""
        return self._call(
            prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            system_instruction=system_instruction,
        )

    def generate_json(
        self,
        prompt: str,
        *,
        temperature: float = 0.0,
        _retry_on_parse_failure: bool = True,
    ) -> dict[str, Any]:
        """Generate a JSON response. Strips markdown fences before parsing.
        On malformed/truncated JSON, makes ONE extra call asking the model
        to correct itself before giving up -- cheap insurance against
        max_output_tokens cutting a response mid-object."""
        text = self._strip_fences(self.generate(prompt, temperature=temperature))
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            fp = _prompt_fingerprint(prompt)
            logger.error("Invalid JSON from Gemini [prompt=%s] len=%d", fp, len(text))
            if _retry_on_parse_failure:
                repair_prompt = (
                    f"{prompt}\n\nYour previous response was not valid JSON or was "
                    f"truncated. Return the COMPLETE, valid JSON object only -- "
                    f"no markdown, no commentary."
                )
                return self.generate_json(
                    repair_prompt, temperature=temperature, _retry_on_parse_failure=False
                )
            raise LLMError("Gemini returned invalid JSON after retry.") from exc

    async def agenerate_json(self, prompt: str, *, temperature: float = 0.0) -> dict[str, Any]:
        """Async wrapper for use inside FastAPI async route handlers --
        runs the blocking SDK call in a thread so it doesn't stall the
        event loop for other concurrent requests."""
        return await asyncio.to_thread(self.generate_json, prompt, temperature=temperature)


# Singleton instance
llm = GeminiClient()