"""Prompt templates for podcast talking-point generation."""

from __future__ import annotations

from podcaster.models import ResearchResult

SYSTEM_PROMPT = """\
You are an expert podcast producer and interviewer. Your job is to analyse \
research about a podcast guest and generate compelling, insightful talking \
points and questions for a podcast episode.

Guidelines:
- Questions should be open-ended and invite storytelling.
- Mix personal-journey questions with expertise-based questions.
- Reference specific things from the research (articles, tweets, projects).
- Consider the target audience when framing questions.
- Include a brief "context" for each question explaining why it's interesting.
- Suggest 2-3 follow-up angles for each main question.
- Order questions from rapport-building to deeper / more challenging topics.

You MUST respond with valid JSON matching this exact schema:
{
  "guest_name": "<string>",
  "guest_summary": "<2-3 sentence summary of the person>",
  "talking_points": [
    {
      "number": <int>,
      "question": "<the question or talking-point statement>",
      "context": "<why this is interesting / relevant>",
      "sources": ["<which research items informed this>"],
      "follow_up_angles": ["<follow-up direction 1>", "<follow-up direction 2>"]
    }
  ],
  "research_summary": "<1-2 paragraph overview of what was found about the person>"
}

Return ONLY the JSON object, no markdown fences, no extra text.\
"""


def build_user_prompt(research: ResearchResult, num_points: int) -> str:
    person = research.person
    sections: list[str] = []

    sections.append(f"Guest name: {person.name}")
    if person.bio:
        sections.append(f"Background: {person.bio}")
    if person.target_audience:
        sections.append(f"Target audience: {person.target_audience}")
    if person.topic:
        sections.append(f"Podcast topic / theme: {person.topic}")

    sections.append(f"\nPlease generate exactly {num_points} talking points.\n")

    # Group research items by source
    by_source: dict[str, list[str]] = {}
    for item in research.items:
        entry_parts = []
        if item.title:
            entry_parts.append(f"Title: {item.title}")
        if item.content:
            entry_parts.append(f"Content: {item.content[:1000]}")
        if item.url:
            entry_parts.append(f"URL: {item.url}")
        if item.date:
            entry_parts.append(f"Date: {item.date}")
        by_source.setdefault(item.source, []).append("\n".join(entry_parts))

    sections.append("=== RESEARCH DATA ===\n")
    for source, entries in by_source.items():
        sections.append(f"--- Source: {source.upper()} ---")
        for i, entry in enumerate(entries, 1):
            sections.append(f"\n[{source} #{i}]\n{entry}")
        sections.append("")

    if not research.items:
        sections.append(
            "(No detailed research was found. Generate talking points based on "
            "the guest's name, background, and topic provided above.)"
        )

    return "\n".join(sections)
