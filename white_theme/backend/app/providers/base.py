"""
Base provider interface for OpportunityOS.

All live providers should inherit from BaseProvider and implement _fetch().
BaseProvider.search() wraps _fetch() with consistent error handling,
normalization, and validation so no provider subclass has to reimplement
that contract itself.

Example:
    - JSearchProvider
    - EventbriteProvider
    - GitHubProvider
    - AdzunaProvider
"""
from __future__ import annotations

import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Any

from app.core.constants import OpportunityType

logger = logging.getLogger(__name__)

_VALID_TYPES = {t.value for t in OpportunityType}
_VALID_TYPES_LOWER = {v.lower(): v for v in _VALID_TYPES}


class ProviderError(Exception):
    """Raised when a provider fails to fetch or parse results. Subclasses
    should catch their own provider-specific exceptions (HTTP errors, bad
    JSON, etc.) and re-raise as ProviderError so callers only ever need
    to handle one exception type regardless of which provider is in use."""


class BaseProvider(ABC):
    """Abstract base class for all opportunity providers."""

    #: Provider name, used as the `source` field on every normalized item
    name: str = "base"

    @abstractmethod
    async def _fetch(
        self,
        *,
        query: str,
        location: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Subclasses implement this: call the external API/scrape the site,
        return a list of RAW (un-normalized) provider-specific dicts.

        Raise ProviderError (or let a provider-specific exception propagate
        -- search() will catch and wrap it) on failure.
        """
        raise NotImplementedError

    async def search(
        self,
        *,
        query: str,
        location: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Public entrypoint. Calls _fetch(), normalizes and validates each
        result, and guarantees a ProviderError (never a provider-internal
        exception) on failure -- callers only need to catch one type.
        """
        try:
            raw_items = await self._fetch(query=query, location=location, limit=limit)
        except ProviderError:
            raise
        except Exception as exc:
            logger.warning("[%s] fetch failed: %s", self.name, exc)
            raise ProviderError(f"{self.name} provider failed: {exc}") from exc

        normalized = []
        for item in raw_items:
            try:
                n = self.normalize(item)
            except Exception:
                logger.exception("[%s] failed to normalize item, skipping", self.name)
                continue
            if self._is_valid(n):
                normalized.append(n)
            else:
                logger.debug("[%s] dropped invalid/incomplete item: %r", self.name, n.get("title"))
        return normalized

    def normalize(self, item: dict[str, Any]) -> dict[str, Any]:
        """Convert a provider-specific raw item into OpportunityOS's
        standard format."""
        title = (item.get("title") or "").strip()
        link = (item.get("apply_link") or "").strip()

        return {
            "id": item.get("id") or self._make_id(title, link),
            "source": self.name,
            "type": self._normalize_type(item.get("type", "")),
            "title": title,
            "company": item.get("company", ""),
            "location": item.get("location", ""),
            "salary": item.get("salary", ""),
            "deadline": item.get("deadline", ""),
            "skills": item.get("skills", []) or [],
            "description": item.get("description", ""),
            "apply_link": link,
            "content_hash": self._make_id(title, link),  # stable dedup key across providers
        }

    @staticmethod
    def _make_id(title: str, link: str) -> str:
        """Stable id/dedup key derived from title+link, used as a fallback
        when a provider gives no id, and always used as content_hash so
        the same listing from two providers can be recognized as a dupe."""
        return hashlib.sha256(f"{link}|{title}".encode()).hexdigest()[:16]

    @staticmethod
    def _normalize_type(raw_type: str) -> str:
        """Maps a provider's free-text type onto OpportunityType, falling
        back to 'unknown' rather than a value that won't match the enum
        anywhere downstream. 'unknown' items can later be classified by
        the LLM classifier, same pattern as the aggregator's classify step."""
        if raw_type in _VALID_TYPES:
            return raw_type
        return _VALID_TYPES_LOWER.get(raw_type.strip().lower(), "unknown")

    @staticmethod
    def _is_valid(item: dict[str, Any]) -> bool:
        """Minimum bar for a usable listing: must have a title and a link.
        Everything else can be empty/unknown and still be useful."""
        return bool(item.get("title")) and bool(item.get("apply_link"))