"""General web search via DuckDuckGo (default) or Serper API."""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

import httpx
from ddgs import DDGS

from podcaster.research.base import BaseResearcher

if TYPE_CHECKING:
    from podcaster.models import PersonInput, ResearchItem


class WebResearcher(BaseResearcher):
    @property
    def source_name(self) -> str:
        return "web"

    def is_available(self) -> bool:
        return True  # DuckDuckGo needs no key

    async def research(self, person: PersonInput) -> list[ResearchItem]:
        from podcaster.models import ResearchItem

        queries = self._build_queries(person)
        if self.settings.serper_api_key:
            return await self._search_serper(queries)
        return await self._search_ddg(queries)

    def _build_queries(self, person: PersonInput) -> list[str]:
        queries = [
            f'"{person.name}"',
            f'"{person.name}" interview',
            f'"{person.name}" podcast',
        ]
        if person.topic:
            queries.append(f'"{person.name}" {person.topic}')
        if person.bio:
            # extract a keyword or two from bio
            queries.append(f'"{person.name}" {person.bio.split(",")[0].strip()}')
        return queries

    # -- DuckDuckGo (no key) ------------------------------------------------

    async def _search_ddg(self, queries: list[str]) -> list[ResearchItem]:
        from podcaster.models import ResearchItem

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
                        source="web",
                        title=r.get("title", ""),
                        content=r.get("body", r.get("snippet", "")),
                        url=url,
                    )
                )
        return items

    @staticmethod
    def _ddg_text(query: str) -> list[dict]:
        return list(DDGS().text(query, max_results=5))

    # -- Serper (optional) ---------------------------------------------------

    async def _search_serper(self, queries: list[str]) -> list[ResearchItem]:
        from podcaster.models import ResearchItem

        items: list[ResearchItem] = []
        seen_urls: set[str] = set()

        async with httpx.AsyncClient(timeout=self.settings.request_timeout) as client:
            for query in queries:
                try:
                    resp = await client.post(
                        "https://google.serper.dev/search",
                        headers={
                            "X-API-KEY": self.settings.serper_api_key,
                            "Content-Type": "application/json",
                        },
                        content=json.dumps({"q": query, "num": 5}),
                    )
                    resp.raise_for_status()
                    data = resp.json()
                except Exception:
                    continue

                for r in data.get("organic", []):
                    url = r.get("link", "")
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    items.append(
                        ResearchItem(
                            source="web",
                            title=r.get("title", ""),
                            content=r.get("snippet", ""),
                            url=url,
                        )
                    )
        return items
