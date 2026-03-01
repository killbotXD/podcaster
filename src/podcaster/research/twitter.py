"""Twitter/X research via web search (no API key required)."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from ddgs import DDGS

from podcaster.research.base import BaseResearcher

if TYPE_CHECKING:
    from podcaster.models import PersonInput, ResearchItem


class TwitterResearcher(BaseResearcher):
    @property
    def source_name(self) -> str:
        return "twitter"

    def is_available(self) -> bool:
        return True

    async def research(self, person: PersonInput) -> list[ResearchItem]:
        from podcaster.models import ResearchItem

        queries = self._build_queries(person)
        items: list[ResearchItem] = []
        seen_urls: set[str] = set()

        for query in queries:
            try:
                results = await asyncio.to_thread(self._ddg_text, query)
            except Exception:
                continue
            for r in results:
                url = r.get("href") or r.get("link", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                items.append(
                    ResearchItem(
                        source="twitter",
                        title=r.get("title", ""),
                        content=r.get("body", r.get("snippet", "")),
                        url=url,
                    )
                )
        return items

    def _build_queries(self, person: PersonInput) -> list[str]:
        queries: list[str] = []
        if person.twitter_handle:
            handle = person.twitter_handle.lstrip("@")
            queries.append(f"site:x.com {handle}")
            queries.append(f"site:twitter.com {handle}")
        else:
            queries.append(f'site:x.com "{person.name}"')
        return queries

    @staticmethod
    def _ddg_text(query: str) -> list[dict]:
        return list(DDGS().text(query, max_results=5))
