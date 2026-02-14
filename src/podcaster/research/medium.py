"""Medium research via RSS feed (primary) with web search fallback."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import feedparser
import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from podcaster.research.base import BaseResearcher

if TYPE_CHECKING:
    from podcaster.models import PersonInput, ResearchItem


class MediumResearcher(BaseResearcher):
    @property
    def source_name(self) -> str:
        return "medium"

    def is_available(self) -> bool:
        return True

    async def research(self, person: PersonInput) -> list[ResearchItem]:
        if person.medium_username:
            items = await self._fetch_rss(person.medium_username)
            if items:
                return items
        # Fallback to web search
        return await self._search_medium(person)

    async def _fetch_rss(self, username: str) -> list[ResearchItem]:
        from podcaster.models import ResearchItem

        username = username.lstrip("@")
        feed_url = f"https://medium.com/feed/@{username}"

        try:
            async with httpx.AsyncClient(
                timeout=self.settings.request_timeout, follow_redirects=True
            ) as client:
                resp = await client.get(feed_url)
                resp.raise_for_status()
                feed_text = resp.text
        except Exception:
            return []

        feed = await asyncio.to_thread(feedparser.parse, feed_text)
        items: list[ResearchItem] = []

        for entry in feed.entries[:10]:
            summary = entry.get("summary", "")
            # Strip HTML from summary
            if summary:
                soup = BeautifulSoup(summary, "lxml")
                summary = soup.get_text(separator=" ", strip=True)[:800]

            items.append(
                ResearchItem(
                    source="medium",
                    title=entry.get("title", ""),
                    content=summary,
                    url=entry.get("link", ""),
                    date=entry.get("published", ""),
                )
            )
        return items

    async def _search_medium(self, person: PersonInput) -> list[ResearchItem]:
        from podcaster.models import ResearchItem

        query = f'site:medium.com "{person.name}"'
        try:
            results = await asyncio.to_thread(self._ddg_text, query)
        except Exception:
            return []

        items: list[ResearchItem] = []
        for r in results:
            items.append(
                ResearchItem(
                    source="medium",
                    title=r.get("title", ""),
                    content=r.get("body", r.get("snippet", "")),
                    url=r.get("href") or r.get("link", ""),
                )
            )
        return items

    @staticmethod
    def _ddg_text(query: str) -> list[dict]:
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=5))
