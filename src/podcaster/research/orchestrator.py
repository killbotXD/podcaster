"""Coordinates all research modules and aggregates results."""

from __future__ import annotations

import asyncio

from rich.console import Console

from podcaster.config import Settings
from podcaster.models import PersonInput, ResearchResult
from podcaster.research.base import BaseResearcher
from podcaster.research.linkedin import LinkedInResearcher
from podcaster.research.medium import MediumResearcher
from podcaster.research.reddit import RedditResearcher
from podcaster.research.twitter import TwitterResearcher
from podcaster.research.web import WebResearcher

console = Console()


class ResearchOrchestrator:
    def __init__(self, settings: Settings) -> None:
        self.researchers: list[BaseResearcher] = [
            WebResearcher(settings),
            TwitterResearcher(settings),
            LinkedInResearcher(settings),
            MediumResearcher(settings),
            RedditResearcher(settings),
        ]

    async def run(self, person: PersonInput) -> ResearchResult:
        available = [r for r in self.researchers if r.is_available()]

        result = ResearchResult(
            person=person,
            sources_attempted=[r.source_name for r in available],
        )

        console.print(
            f"\n[bold]Researching {person.name}[/bold] across "
            f"{len(available)} sources...\n"
        )

        # Run all researchers concurrently
        tasks = {
            r.source_name: asyncio.create_task(r.research(person)) for r in available
        }

        for name, task in tasks.items():
            try:
                items = await task
                if items:
                    result.items.extend(items)
                    result.sources_succeeded.append(name)
                    console.print(f"  [green]✓[/green] {name}: {len(items)} items")
                else:
                    result.sources_failed[name] = "no results"
                    console.print(f"  [yellow]–[/yellow] {name}: no results")
            except Exception as exc:
                result.sources_failed[name] = str(exc)
                console.print(f"  [red]✗[/red] {name}: {exc}")

        # Deduplicate by URL
        seen_urls: set[str] = set()
        unique_items = []
        for item in result.items:
            key = item.url or item.content[:100]
            if key not in seen_urls:
                seen_urls.add(key)
                unique_items.append(item)
        result.items = unique_items

        console.print(
            f"\n[bold]Research complete:[/bold] {len(result.items)} unique items "
            f"from {len(result.sources_succeeded)} sources\n"
        )
        return result
