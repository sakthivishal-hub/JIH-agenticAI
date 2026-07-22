"""
Provider Manager for OpportunityOS.

Responsible for:
- Registering providers
- Running searches concurrently
- Merging results
- Removing duplicates
- Handling provider failures
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class ProviderManager:

    def __init__(self) -> None:
        self._providers: list[BaseProvider] = []

    def register(self, provider: BaseProvider) -> None:
        """Register a new provider."""

        if any(p.name == provider.name for p in self._providers):
            logger.warning("Provider '%s' already registered.", provider.name)
            return

        self._providers.append(provider)
        logger.info("Registered provider: %s", provider.name)

    @property
    def providers(self) -> list[BaseProvider]:
        return self._providers

    async def search(
        self,
        *,
        query: str,
        location: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:

        if not self._providers:
            return []

        tasks = [
            provider.search(
                query=query,
                location=location,
                limit=limit,
            )
            for provider in self._providers
        ]

        responses = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        opportunities: list[dict[str, Any]] = []

        for provider, response in zip(self._providers, responses):

            if isinstance(response, Exception):
                logger.exception(
                    "Provider '%s' failed.",
                    provider.name,
                )
                continue

            opportunities.extend(response)

        return self._deduplicate(opportunities)[:limit]

    @staticmethod
    def _deduplicate(
        opportunities: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:

        seen: set[tuple[str, str, str]] = set()
        unique: list[dict[str, Any]] = []

        for item in opportunities:

            key = (
                item.get("title", ""),
                item.get("company", ""),
                item.get("type", ""),
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(item)

        return unique


provider_manager = ProviderManager()