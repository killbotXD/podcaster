"""Typer CLI entry point — the main `podcaster` command."""

from __future__ import annotations

import asyncio
import sys

import typer
from rich.console import Console

app = typer.Typer(
    name="podcaster",
    help="Research a podcast guest online and generate talking points.",
    add_completion=False,
)
console = Console(stderr=True)


@app.command()
def research(
    name: str = typer.Argument(..., help="Full name of the podcast guest"),
    bio: str = typer.Option(None, "--bio", "-b", help="Brief background / bio"),
    linkedin: str = typer.Option(None, "--linkedin", help="LinkedIn profile URL"),
    twitter: str = typer.Option(None, "--twitter", help="Twitter/X handle (e.g. @user)"),
    medium: str = typer.Option(None, "--medium", help="Medium username (without @)"),
    reddit: str = typer.Option(None, "--reddit", help="Reddit username (without u/)"),
    audience: str = typer.Option(None, "--audience", "-a", help="Target audience description"),
    topic: str = typer.Option(None, "--topic", "-t", help="Podcast topic or theme"),
    output_format: str = typer.Option(
        "markdown", "--format", "-f", help="Output format: console, json, markdown"
    ),
    num_points: int = typer.Option(5, "--num-points", "-n", help="Number of talking points"),
    output_file: str = typer.Option(None, "--output", "-o", help="Write output to a file"),
) -> None:
    """Research a person and generate podcast talking points."""
    from podcaster.config import Settings
    from podcaster.generation.generator import TalkingPointGenerator
    from podcaster.models import PersonInput
    from podcaster.output.formatter import format_console, format_json, format_markdown
    from podcaster.research.orchestrator import ResearchOrchestrator

    # ── Load settings ───────────────────────────────────────────────
    try:
        settings = Settings()  # type: ignore[call-arg]
    except Exception as exc:
        console.print(f"[red]Configuration error:[/red] {exc}")
        raise typer.Exit(1)

    if not settings.anthropic_api_key:
        console.print(
            "[red]PODCASTER_ANTHROPIC_API_KEY is required.[/red]\n"
            "Set it in your environment or in a .env file.\n"
            "See .env.example for details."
        )
        raise typer.Exit(1)

    # ── Build input model ───────────────────────────────────────────
    person = PersonInput(
        name=name,
        bio=bio,
        linkedin_url=linkedin,
        twitter_handle=twitter,
        medium_username=medium,
        reddit_username=reddit,
        target_audience=audience,
        topic=topic,
    )

    # ── Research phase ──────────────────────────────────────────────
    orchestrator = ResearchOrchestrator(settings)
    research_result = asyncio.run(orchestrator.run(person))

    # ── Generation phase ────────────────────────────────────────────
    generator = TalkingPointGenerator(settings)
    try:
        brief = generator.generate(research_result, num_points=num_points)
    except Exception as exc:
        console.print(f"[red]Generation failed:[/red] {exc}")
        raise typer.Exit(1)

    # ── Output ──────────────────────────────────────────────────────
    if output_format == "json":
        text = format_json(brief)
        if output_file:
            _write_file(output_file, text)
        else:
            print(text)
    elif output_format == "markdown":
        text = format_markdown(brief)
        dest = output_file or _default_filename(name, "md")
        _write_file(dest, text)
        # Also show a summary on the console
        format_console(brief)
    else:
        format_console(brief)
        if output_file:
            _write_file(output_file, format_markdown(brief))
            console.print(f"\n[dim]Also saved to {output_file}[/dim]")


def _default_filename(guest_name: str, ext: str) -> str:
    slug = guest_name.lower().replace(" ", "_")
    return f"podcast_brief_{slug}.{ext}"


def _write_file(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)
    Console(stderr=True).print(f"[green]Output written to {path}[/green]")
