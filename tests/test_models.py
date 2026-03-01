"""Tests for data models."""

from podcaster.models import PodcastBrief, PersonInput, ResearchItem, ResearchResult, TalkingPoint


def test_person_input_minimal():
    p = PersonInput(name="John Doe")
    assert p.name == "John Doe"
    assert p.bio is None
    assert p.twitter_handle is None


def test_person_input_full():
    p = PersonInput(
        name="Jane Smith",
        bio="AI researcher",
        linkedin_url="https://linkedin.com/in/janesmith",
        twitter_handle="@janesmith",
        medium_username="janesmith",
        reddit_username="janesmith_ai",
        target_audience="Engineers",
        topic="AI",
    )
    assert p.name == "Jane Smith"
    assert p.twitter_handle == "@janesmith"


def test_research_item():
    item = ResearchItem(
        source="web",
        title="Test Article",
        content="Some content here",
        url="https://example.com",
    )
    assert item.source == "web"
    assert item.url == "https://example.com"


def test_research_result_empty():
    person = PersonInput(name="Test Person")
    result = ResearchResult(person=person)
    assert result.items == []
    assert result.sources_succeeded == []


def test_talking_point():
    tp = TalkingPoint(
        number=1,
        question="What inspired you?",
        context="Based on their background",
        sources=["web #1"],
        follow_up_angles=["Early career", "Key mentors"],
    )
    assert tp.number == 1
    assert len(tp.follow_up_angles) == 2


def test_podcast_brief():
    brief = PodcastBrief(
        guest_name="Jane Smith",
        guest_summary="AI researcher at Stanford.",
        talking_points=[
            TalkingPoint(
                number=1,
                question="Tell us about your journey",
                context="Background question",
            )
        ],
        research_summary="Found 3 articles.",
    )
    assert brief.guest_name == "Jane Smith"
    assert len(brief.talking_points) == 1
