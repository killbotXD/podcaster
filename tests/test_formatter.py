"""Tests for output formatting."""

from podcaster.models import PodcastBrief, TalkingPoint
from podcaster.output.formatter import format_json, format_markdown


def _make_brief():
    return PodcastBrief(
        guest_name="Jane Smith",
        guest_summary="AI researcher at Stanford specialising in LLMs.",
        talking_points=[
            TalkingPoint(
                number=1,
                question="What sparked your interest in AI?",
                context="Opens with personal journey",
                sources=["web #1"],
                follow_up_angles=["Early influences", "Key turning points"],
            ),
            TalkingPoint(
                number=2,
                question="How do you see LLMs changing software engineering?",
                context="Core expertise area",
                sources=["medium #1"],
                follow_up_angles=["Specific tools", "Risks"],
            ),
        ],
        research_summary="Found articles across web and Medium.",
    )


def test_format_json():
    brief = _make_brief()
    output = format_json(brief)
    import json

    data = json.loads(output)
    assert data["guest_name"] == "Jane Smith"
    assert len(data["talking_points"]) == 2


def test_format_markdown():
    brief = _make_brief()
    md = format_markdown(brief)
    assert "# Podcast Brief: Jane Smith" in md
    assert "## Talking Points" in md
    assert "What sparked your interest in AI?" in md
    assert "Early influences" in md
