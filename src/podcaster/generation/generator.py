"""Claude API integration for generating podcast talking points."""

from __future__ import annotations

import json

import anthropic
from rich.console import Console

from podcaster.config import Settings
from podcaster.generation.prompt import SYSTEM_PROMPT, build_user_prompt
from podcaster.models import PodcastBrief, ResearchResult

console = Console()


class TalkingPointGenerator:
    def __init__(self, settings: Settings) -> None:
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model

    def generate(self, research: ResearchResult, num_points: int = 5) -> PodcastBrief:
        user_prompt = build_user_prompt(research, num_points)

        console.print("[bold]Generating talking points with Claude...[/bold]\n")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = response.content[0].text

        # Parse the JSON response
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown fences if present
            import re

            match = re.search(r"```(?:json)?\s*(.*?)```", raw_text, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
            else:
                raise ValueError(f"Could not parse LLM response as JSON:\n{raw_text[:500]}")

        return PodcastBrief.model_validate(data)
