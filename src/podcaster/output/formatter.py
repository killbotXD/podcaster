"""Output formatting for podcast briefs (console, JSON, Markdown)."""

from __future__ import annotations

import json

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from podcaster.models import PodcastBrief

console = Console()


def format_console(brief: PodcastBrief) -> None:
    """Pretty-print the podcast brief to the terminal."""

    # Guest summary panel
    console.print(
        Panel(
            brief.guest_summary,
            title=f"[bold]{brief.guest_name}[/bold]",
            border_style="cyan",
        )
    )
    console.print()

    # Research summary
    console.print("[bold underline]Research Summary[/bold underline]")
    console.print(brief.research_summary)
    console.print()

    # Talking points
    console.print("[bold underline]Talking Points[/bold underline]\n")
    for tp in brief.talking_points:
        console.print(f"[bold cyan]#{tp.number}[/bold cyan] [bold]{tp.question}[/bold]")
        console.print(f"  [dim]Context:[/dim] {tp.context}")
        if tp.sources:
            console.print(f"  [dim]Sources:[/dim] {', '.join(tp.sources)}")
        if tp.follow_up_angles:
            console.print(f"  [dim]Follow-ups:[/dim]")
            for angle in tp.follow_up_angles:
                console.print(f"    • {angle}")
        console.print()


def format_json(brief: PodcastBrief) -> str:
    """Return the brief as a JSON string."""
    return brief.model_dump_json(indent=2)


def format_markdown(brief: PodcastBrief) -> str:
    """Return the brief as a Markdown document."""
    lines: list[str] = []
    lines.append(f"# Podcast Brief: {brief.guest_name}\n")
    lines.append(f"## Guest Summary\n\n{brief.guest_summary}\n")
    lines.append(f"## Research Summary\n\n{brief.research_summary}\n")
    lines.append("## Talking Points\n")

    for tp in brief.talking_points:
        lines.append(f"### {tp.number}. {tp.question}\n")
        lines.append(f"**Context:** {tp.context}\n")
        if tp.sources:
            lines.append(f"**Sources:** {', '.join(tp.sources)}\n")
        if tp.follow_up_angles:
            lines.append("**Follow-up angles:**\n")
            for angle in tp.follow_up_angles:
                lines.append(f"- {angle}")
            lines.append("")
        lines.append("")

    return "\n".join(lines)
