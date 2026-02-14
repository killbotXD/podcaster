"""Reddit research via PRAW (official API) with web search fallback."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from duckduckgo_search import DDGS

from podcaster.research.base import BaseResearcher

if TYPE_CHECKING:
    from podcaster.models import PersonInput, ResearchItem


class RedditResearcher(BaseResearcher):
    @property
    def source_name(self) -> str:
        return "reddit"

    def is_available(self) -> bool:
        return True  # Falls back to web search if no creds

    async def research(self, person: PersonInput) -> list[ResearchItem]:
        has_creds = bool(
            self.settings.reddit_client_id and self.settings.reddit_client_secret
        )
        if has_creds and person.reddit_username:
            items = await self._fetch_praw(person.reddit_username)
            if items:
                return items

        return await self._search_reddit(person)

    async def _fetch_praw(self, username: str) -> list[ResearchItem]:
        from podcaster.models import ResearchItem

        username = username.lstrip("u/").lstrip("/u/")

        try:
            import praw

            reddit = praw.Reddit(
                client_id=self.settings.reddit_client_id,
                client_secret=self.settings.reddit_client_secret,
                user_agent=self.settings.reddit_user_agent,
            )
            reddit.read_only = True

            items: list[ResearchItem] = []

            def _gather():
                redditor = reddit.redditor(username)
                # Top submissions
                for submission in redditor.submissions.top(limit=10):
                    body = submission.selftext[:600] if submission.selftext else ""
                    items.append(
                        ResearchItem(
                            source="reddit",
                            title=f"[r/{submission.subreddit.display_name}] {submission.title}",
                            content=body or submission.title,
                            url=f"https://reddit.com{submission.permalink}",
                        )
                    )
                # Top comments
                for comment in redditor.comments.top(limit=10):
                    items.append(
                        ResearchItem(
                            source="reddit",
                            title=f"Comment in r/{comment.subreddit.display_name}",
                            content=comment.body[:600],
                            url=f"https://reddit.com{comment.permalink}",
                        )
                    )

            await asyncio.to_thread(_gather)
            return items
        except Exception:
            return []

    async def _search_reddit(self, person: PersonInput) -> list[ResearchItem]:
        from podcaster.models import ResearchItem

        query = f'site:reddit.com "{person.name}"'
        try:
            results = await asyncio.to_thread(self._ddg_text, query)
        except Exception:
            return []

        items: list[ResearchItem] = []
        for r in results:
            items.append(
                ResearchItem(
                    source="reddit",
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
