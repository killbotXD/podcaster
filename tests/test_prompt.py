"""Tests for prompt building."""

from podcaster.generation.prompt import build_user_prompt


def test_build_user_prompt_with_research(sample_research):
    prompt = build_user_prompt(sample_research, num_points=5)
    assert "Jane Smith" in prompt
    assert "5 talking points" in prompt
    assert "RESEARCH DATA" in prompt
    assert "WEB" in prompt
    assert "MEDIUM" in prompt
    assert "TWITTER" in prompt


def test_build_user_prompt_empty_research(sample_person):
    from podcaster.models import ResearchResult

    empty = ResearchResult(person=sample_person)
    prompt = build_user_prompt(empty, num_points=3)
    assert "Jane Smith" in prompt
    assert "3 talking points" in prompt
    assert "No detailed research was found" in prompt


def test_build_user_prompt_includes_audience(sample_research):
    prompt = build_user_prompt(sample_research, num_points=5)
    assert "Software engineers interested in AI" in prompt


def test_build_user_prompt_includes_topic(sample_research):
    prompt = build_user_prompt(sample_research, num_points=5)
    assert "Practical applications of LLMs" in prompt
