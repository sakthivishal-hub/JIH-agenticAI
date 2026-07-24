"""
Opportunity Search Agent.

Coordinates multiple opportunity providers and returns
a unified opportunity list.
"""

from __future__ import annotations

import asyncio
from typing import Any, Iterable


class SearchAgentError(Exception):
    """Raised when searching opportunities fails."""


class BaseProvider:
    """Base class for all providers."""

    name = "base"

    async def search(
        self,
        *,
        query: str,
        location: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError


class SearchAgent:

    def __init__(self) -> None:
        self.providers: list[BaseProvider] = []

    # --------------------------------------------------
    # Provider registration
    # --------------------------------------------------

    def register(self, provider: BaseProvider) -> None:
        """Register a search provider."""
        self.providers.append(provider)

    # --------------------------------------------------
    # Public search
    # --------------------------------------------------

    async def search(
        self,
        *,
        query: str,
        location: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:

        if not self.providers:
            return []

        tasks = [
            provider.search(
                query=query,
                location=location,
                limit=limit,
            )
            for provider in self.providers
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        opportunities: list[dict[str, Any]] = []

        for provider, result in zip(self.providers, results):

            if isinstance(result, Exception):
                print(f"{provider.name} failed: {result}")
                continue

            opportunities.extend(result)

        opportunities = self._deduplicate(opportunities)

        opportunities.sort(
            key=lambda x: x.get("deadline", ""),
            reverse=False,
        )

        return opportunities[:limit]

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------

    @staticmethod
    def _deduplicate(
        opportunities: Iterable[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        seen = set()
        unique = []

        for item in opportunities:

            key = (
                item.get("title", ""),
                item.get("company", ""),
                item.get("apply_link", ""),
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(item)

        return unique


search_agent = SearchAgent()